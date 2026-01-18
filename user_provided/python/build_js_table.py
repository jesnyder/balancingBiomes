import json
from pathlib import Path

def build_js_table():
    # -------------------------------
    # Paths
    # -------------------------------
    json_file = Path("results/search_results/list_compiled.json")
    output_js_file = Path("docs/js/most_cited.js")
    output_js_file.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------
    # Load JSON
    # -------------------------------
    with open(json_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # -------------------------------
    # Sort by citations
    # -------------------------------
    def citation_count(article):
        return int(article.get("cited_by", article.get("is_referenced_by_count", 0)) or 0)

    articles_sorted = sorted(articles, key=citation_count, reverse=True)[:200]

    # -------------------------------
    # Select only the fields for table
    # -------------------------------
    # Example fields: title, authors, year, journal, citations, url
    table_data = []
    for a in articles_sorted:
        table_data.append({
            "title": a.get("title", ""),
            "authors": a.get("authors", ""),
            "year": a.get("year", ""),
            "journal": a.get("journal", ""),
            "citations": citation_count(a),
            "url": a.get("url", "")
        })

    # -------------------------------
    # Generate JS file
    # -------------------------------
    js_content = f"""/*
===========================================================
MOST CITED RESEARCH TABLE — TABULATOR SETUP
===========================================================

REQUIRED HTML (paste this in index.html):

1️⃣ Include Tabulator CSS + JS (once):
-----------------------------------------------------------
<link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>

2️⃣ Add button + table container:
-----------------------------------------------------------
<button id="download-most-cited">Download Table</button>
<div id="most-cited-research-table"></div>

3️⃣ Include this JS file AFTER the div:
-----------------------------------------------------------
<script src="docs/js/most_cited.js"></script>

WHY:
- Tabulator requires the div to exist before initialization
- Data is embedded directly (no AJAX)
- Avoids 404 and CORS issues
===========================================================
*/

document.addEventListener("DOMContentLoaded", function() {{

    const tableData = {json.dumps(table_data, indent=4)};

    const table = new Tabulator("#most-cited-research-table", {{
        data: tableData,
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 15,
        movableColumns: true,
        columns: [
            {{
                title: "Title",
                field: "title",
                formatter: function(cell) {{
                    const val = cell.getValue();
                    const url = cell.getRow().getData().url;
                    if (url) {{
                        return `<a href="${{url}}" target="_blank">${{val}}</a>`;
                    }}
                    return val;
                }},
                headerFilter: "input"
            }},
            {{
                title: "Authors",
                field: "authors",
                headerFilter: "input"
            }},
            {{
                title: "Year",
                field: "year",
                sorter: "number",
                headerFilter: "input"
            }},
            {{
                title: "Journal",
                field: "journal",
                headerFilter: "input"
            }},
            {{
                title: "Citations",
                field: "citations",
                sorter: "number",
                headerFilter: "input"
            }}
        ]
    }});

    // Download button
    document.getElementById("download-most-cited").addEventListener("click", function() {{
        table.download("csv", "most_cited_research.csv");
    }});
}});
"""

    # Write JS file
    with open(output_js_file, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"Generated JS table: {output_js_file}")


if __name__ == "__main__":
    build_js_table()
