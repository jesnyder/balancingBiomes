#!/usr/bin/env python3
"""
count_species.py

Single-file pipeline that:
- Reads species list
- Scans article corpus
- Counts species mentions
- Computes citation-aware metrics
- Writes JSON + CSV
- Generates a complete Tabulator JS file

No external dependencies.
"""

import json
import os
import csv

SPECIES_FILE = "results/species_detailed.json"
ARTICLES_FILE = "results/search_results/list_compiled.json"

OUT_DIR = "results/species_found"
OUT_JSON = f"{OUT_DIR}/species_frequency.json"
OUT_CSV = f"{OUT_DIR}/species_frequency.csv"

JS_DIR = "docs/js"
JS_FILE = f"{JS_DIR}/species_found.js"


def extract_article_text(article):
    text = []
    for k, v in article.items():
        if k == "reference":
            continue
        if isinstance(v, str):
            text.append(v)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, str):
                    text.append(x)
        elif isinstance(v, dict):
            for x in v.values():
                if isinstance(x, str):
                    text.append(x)
    return " ".join(text).lower()


def count_species():
    print("\n=== Loading input files ===")

    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"Species loaded: {len(species_list)}")
    print(f"Articles loaded: {len(articles)}")

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(JS_DIR, exist_ok=True)

    print("\n=== Preprocessing articles ===")

    article_texts = []
    citation_counts = []

    for art in articles:
        article_texts.append(extract_article_text(art))

        c = art.get("cited_by") or art.get("is_referenced_by_count") or 0
        try:
            c = int(c)
        except:
            c = 0

        citation_counts.append(c)

    total_articles = len(article_texts)
    total_2plus = sum(1 for c in citation_counts if c >= 2)

    print(f"Articles with ≥2 citations: {total_2plus}")

    results = []

    print("\n=== Counting species ===")

    for i, entry in enumerate(species_list, 1):
        name = entry.get("species") or entry.get("name")
        if not name:
            continue

        name_lc = name.lower()

        found = 0
        found_2plus = 0

        for idx, text in enumerate(article_texts):
            if name_lc in text:
                found += 1
                if citation_counts[idx] >= 2:
                    found_2plus += 1

        pct = round((found / total_articles) * 100, 2) if total_articles else 0
        pct2 = round((found_2plus / total_2plus) * 100, 2) if total_2plus else 0

        entry["article_count"] = found
        entry["article_pct"] = pct
        entry["article_morethan2_count"] = found_2plus
        entry["article_morethan2_pct"] = pct2

        print(f"[{i:4}] {name:<40} → {found} articles")

        results.append(entry)

    results.sort(key=lambda x: x["article_count"], reverse=True)

    print("\n=== Writing JSON & CSV ===")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "species",
                "article_count",
                "article_pct",
                "article_morethan2_count",
                "article_morethan2_pct",
            ],
        )
        writer.writeheader()
        for r in results:
            writer.writerow({
                "species": r.get("species", ""),
                "article_count": r["article_count"],
                "article_pct": r["article_pct"],
                "article_morethan2_count": r["article_morethan2_count"],
                "article_morethan2_pct": r["article_morethan2_pct"],
            })

    print("JSON + CSV written.")

    print("\n=== Writing Tabulator JS ===")

    js_data = json.dumps(results, indent=2)

    js_code = f"""
/*
====================================================
species_found.js

Include in HTML:

<link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>

<button id="downloadCSV">Download CSV</button>
<div id="species_found"></div>
<script src="docs/js/species_found.js"></script>
====================================================
*/

const speciesFound = {js_data};

const speciesTable = new Tabulator("#species_found", {{
    data: speciesFound,
    layout: "fitDataStretch",
    pagination: "local",
    paginationSize: 20,
    movableColumns: true,

    columns: [
        {{ title: "Species", field: "species", headerFilter: "input", widthGrow: 3 }},
        {{ title: "Articles", field: "article_count", sorter: "number", width: "15%", headerFilter: "number" }},
        {{ title: "% of Articles", field: "article_pct", sorter: "number", width: "15%", headerFilter: "number" }},
        {{ title: "≥2 Citations", field: "article_morethan2_count", sorter: "number", width: "15%", headerFilter: "number" }},
        {{ title: "% ≥2 Citations", field: "article_morethan2_pct", sorter: "number", width: "15%", headerFilter: "number" }}
    ]
}});

document.getElementById("downloadCSV").addEventListener("click", function () {{
    speciesTable.download("csv", "species_frequency.csv");
}});
"""

    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write(js_code)

    print(f"JS written → {JS_FILE}")
    print("\n✅ DONE")


if __name__ == "__main__":
    count_species()
