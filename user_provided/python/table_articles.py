#!/usr/bin/env python3
"""
Date: 2026-02-22

Objective:
    Build a searchable and sortable interactive table using Tabulator
    from compiled article metadata. Handles DOI URLs, fallback links,
    and validates URLs to avoid broken links.

Dependencies:
    - json       (reading and saving article data)
    - os         (directory/file handling)
    - requests   (HTTP HEAD requests to check URLs)

Design Notes:
    • Written for clarity and novice understanding
    • Handles 'link' as dict or list of dicts
    • Checks DOI URL first; falls back to other URLs
    • Prints progress updates for troubleshooting
"""

import os
import json
import requests

def table_articles():
    """Main function to build the Tabulator JS table."""

    input_file = "results/query/compiled_articles.json"
    output_js = "docs/js/tableArticles.js"

    print("Loading compiled articles...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    total_articles = len(articles)
    print(f"Loaded {total_articles} articles.")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_js), exist_ok=True)

    table_data = []

    for idx, article in enumerate(articles, start=1):
        # ---------------------------
        # Determine the URL to use
        # ---------------------------
        doi_url = article.get("doi_url")
        link_field = article.get("link")
        fallback_urls = []

        # Handle 'link' field being dict or list
        if isinstance(link_field, dict):
            fallback_urls.append(link_field.get("url"))
        elif isinstance(link_field, list):
            for item in link_field:
                if isinstance(item, dict) and "url" in item:
                    fallback_urls.append(item["url"])

        # Add pub_url as another fallback
        fallback_urls.append(article.get("pub_url"))

        url_to_use = None

        # First try DOI URL
        if doi_url:
            try:
                r = requests.head(doi_url, allow_redirects=True, timeout=5)
                if 200 <= r.status_code < 400:
                    url_to_use = doi_url
            except:
                pass

        # Then try fallback URLs
        if not url_to_use:
            for u in fallback_urls:
                if u:
                    try:
                        r = requests.head(u, allow_redirects=True, timeout=5)
                        if 200 <= r.status_code < 400:
                            url_to_use = u
                            break
                    except:
                        continue

        # ---------------------------
        # Prepare table row
        # ---------------------------
        bib = article.get("bib", {})
        title = bib.get("title", "No title")
        title_link = url_to_use if url_to_use else "#"
        container_type = article.get("container_type", "N/A")
        pub_year = article.get("pub_year", "N/A")
        citations = article.get("is-referenced-by-count")
        if citations is None:
            citations = article.get("num_citations", 0)

        row = {
            "Title": f'<a href="{title_link}" target="_blank">{title}</a>',
            "Type": container_type,
            "Year": pub_year,
            "Citations": citations
        }
        table_data.append(row)

        # Progress feedback
        if idx % 100 == 0 or idx == total_articles:
            print(f"Processed {idx}/{total_articles} articles...")

    # ---------------------------
    # Build JS table file
    # ---------------------------
    js_content = f"""
// Auto-generated Tabulator table
// Date: 2026-02-22
// Variable: tableArticlesData
var tableArticlesData = {json.dumps(table_data, indent=2, ensure_ascii=False)};

// Create Tabulator table
var tableArticles = new Tabulator("#tableArticles", {{
    data: tableArticlesData,
    layout:"fitColumns",
    pagination:"local",
    paginationSize:20,
    columns:[
        {{title:"Title", field:"Title", headerFilter:"input"}},
        {{title:"Type", field:"Type", headerFilter:"input"}},
        {{title:"Year", field:"Year", sorter:"number", headerFilter:"input"}},
        {{title:"Citations", field:"Citations", sorter:"number", headerFilter:"input"}}
    ]
}});

// Add download button
document.getElementById("downloadArticles").addEventListener("click", function(){{
    tableArticles.download("csv", "articles_table.csv");
}});
"""

    with open(output_js, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\nJS table data saved → {output_js}")
    print("=== Done ===\n")


# ---------------------------
# Run script
# ---------------------------
if __name__ == "__main__":
    table_articles()
