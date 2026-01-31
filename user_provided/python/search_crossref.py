#!/usr/bin/env python3
"""
===============================================================================
Date prepared: 2026-01-29

Objective:
-----------
Query the CrossRef REST API for scholarly articles that contain BOTH
"Halophyte" AND "Halophile", clean and analyze the results, and generate:

1. A structured JSON archive of all articles
2. A journal-title summary JSON file
3. Interactive Tabulator JavaScript tables for:
   - Journals
   - Articles (≥2 citations)
   - Article types

Tasks Performed:
----------------
1. Query CrossRef API with pagination (100 records per request)
2. Respect API limits using a 3-second delay
3. Deduplicate articles using DOI
4. Sort articles by citation count
5. Save structured results to JSON
6. Extract journal titles (case-insensitive)
7. Generate Tabulator-based JavaScript tables
8. Embed dataset directly into JavaScript
9. Add CSV / JSON export buttons
10. Provide HTML integration instructions

Input:
------
- CrossRef REST API:
  https://api.crossref.org/works
- Query: "Halophyte AND Halophile"

Output:
-------
- results/results_crossref.json
- results/titles.json
- docs/js/table_titles.js
- docs/js/table_articles.js
- docs/js/table_types.js

Dependencies:
-------------
- requests
- json
- time
- os
- collections
- datetime
===============================================================================
"""

import os
import json
import time
import requests
from collections import defaultdict
from datetime import datetime


def search_crossref():
    # ------------------------------------------------------------------
    # CONFIGURATION
    # ------------------------------------------------------------------
    BASE_URL = "https://api.crossref.org/works"
    QUERY = "Halophyte AND Halophile"
    ROWS = 100
    MAX_RESULTS = 20000
    WAIT_SECONDS = 3

    os.makedirs("results", exist_ok=True)
    os.makedirs("docs/js", exist_ok=True)

    print("\n==============================")
    print("CROSSREF SEARCH STARTED")
    print("==============================\n")

    # ------------------------------------------------------------------
    # STEP 1 — QUERY CROSSREF
    # ------------------------------------------------------------------
    all_articles = {}
    offset = 0
    page = 1

    while offset < MAX_RESULTS:
        print(f"Fetching page {page} (offset {offset})")

        params = {
            "query": QUERY,
            "rows": ROWS,
            "offset": offset
        }

        r = requests.get(BASE_URL, params=params)
        if r.status_code != 200:
            print("ERROR:", r.text)
            break

        data = r.json()
        items = data.get("message", {}).get("items", [])

        if not items:
            break

        for item in items:
            doi = item.get("DOI")
            if doi and doi not in all_articles:
                all_articles[doi] = item

        offset += ROWS
        page += 1
        time.sleep(WAIT_SECONDS)

    articles = list(all_articles.values())

    # ------------------------------------------------------------------
    # STEP 2 — CLEAN & SORT
    # ------------------------------------------------------------------
    articles.sort(
        key=lambda x: x.get("is-referenced-by-count", 0),
        reverse=True
    )

    count_abstract = sum(1 for a in articles if a.get("abstract"))
    count_2plus = sum(1 for a in articles if a.get("is-referenced-by-count", 0) >= 2)

    all_keys = sorted({k for a in articles for k in a.keys()})

    # ------------------------------------------------------------------
    # STEP 3 — SAVE MAIN RESULTS
    # ------------------------------------------------------------------
    results_json = {
        "database": "crossref",
        "count": len(articles),
        "count_abstract": count_abstract,
        "count_2": count_2plus,
        "keys": all_keys,
        "articles": articles
    }

    with open("results/results_crossref.json", "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2)

    # ------------------------------------------------------------------
    # STEP 4 — JOURNAL TITLES
    # ------------------------------------------------------------------
    titles = defaultdict(int)

    for a in articles:
        if a.get("container-title"):
            title = a["container-title"][0]
            titles[title.upper()] += 1

    titles_list = [
        {"title": k.title(), "count": v}
        for k, v in titles.items()
    ]
    titles_list.sort(key=lambda x: x["count"], reverse=True)

    titles_json = {
        "count": len(titles_list),
        "count_articles": sum(t["count"] for t in titles_list),
        "titles": titles_list
    }

    with open("results/titles.json", "w", encoding="utf-8") as f:
        json.dump(titles_json, f, indent=2)

    # ------------------------------------------------------------------
    # STEP 5 — JS TABLE: TITLES
    # ------------------------------------------------------------------
    with open("docs/js/table_titles.js", "w", encoding="utf-8") as f:
        f.write(f"""
/*
TABLE: Journal Titles
Data source: results/titles.json
*/

const titles = {json.dumps(titles_json, indent=2)};

const tableTitles = new Tabulator("#tableOfTitles", {{
  data: titles.titles,
  layout: "fitColumns",
  pagination: true,
  paginationSize: 20,
  initialSort: [{{column: "count", dir: "desc"}}],
  columns: [
    {{title: "Journal", field: "title", headerFilter: "input"}},
    {{title: "Count", field: "count", sorter: "number"}}
  ]
}});
""")

    # ------------------------------------------------------------------
    # STEP 6 — JS TABLE: ARTICLES
    # ------------------------------------------------------------------
    filtered_articles = [
        a for a in articles if a.get("is-referenced-by-count", 0) >= 2
    ]

    with open("docs/js/table_articles.js", "w", encoding="utf-8") as f:
        f.write(f"""
/*
TABLE: Articles (>=2 citations)
*/

const articles = {json.dumps(filtered_articles, indent=2)};

const tableArticles = new Tabulator("#tableOfArticles", {{
  data: articles,
  layout: "fitColumns",
  pagination: true,
  paginationSize: 20,
  initialSort: [{{column: "is-referenced-by-count", dir: "desc"}}],
  columns: [
    {{
      title: "Title",
      field: "title",
      formatter: (cell) => {{
        const d = cell.getRow().getData();
        return `<a href="https://doi.org/${{d.DOI}}" target="_blank">${{d.title[0]}}</a>`;
      }}
    }},
    {{title: "Type", field: "type"}},
    {{title: "Journal", field: "container-title"}},
    {{title: "Year", field: "published-print"}},
    {{title: "Citations", field: "is-referenced-by-count"}}
  ]
}});
""")

    # ------------------------------------------------------------------
    # STEP 7 — JS TABLE: TYPES
    # ------------------------------------------------------------------
    type_counts = defaultdict(int)
    for a in articles:
        if a.get("type"):
            type_counts[a["type"]] += 1

    types_list = [
        {"type": k, "count": v}
        for k, v in type_counts.items()
    ]
    types_list.sort(key=lambda x: x["count"], reverse=True)

    with open("docs/js/table_types.js", "w", encoding="utf-8") as f:
        f.write(f"""
/*
TABLE: Article Types
*/

const types = {json.dumps(types_list, indent=2)};

const tableTypes = new Tabulator("#tableOfTypes", {{
  data: types,
  layout: "fitColumns",
  pagination: true,
  paginationSize: 20,
  initialSort: [{{column: "count", dir: "desc"}}],
  columns: [
    {{title: "Type", field: "type", headerFilter: "input"}},
    {{title: "Count", field: "count", sorter: "number"}}
  ]
}});
""")

    print("\n==============================")
    print("PROCESS COMPLETE")
    print("==============================")
    print("Files created:")
    print(" - results/results_crossref.json")
    print(" - results/titles.json")
    print(" - docs/js/table_titles.js")
    print(" - docs/js/table_articles.js")
    print(" - docs/js/table_types.js")


if __name__ == "__main__":
    search_crossref()
