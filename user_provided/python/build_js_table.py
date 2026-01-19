import json
from pathlib import Path


def build_js_table():
    INPUT_JSON = Path("results/search_results/list_compiled.json")
    OUTPUT_DIR = Path("docs/js")
    OUTPUT_FILE = OUTPUT_DIR / "most_cited.js"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_JSON}")

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []

    for entry in data:
        cleaned.append({
            "title": (entry.get("title") or "").strip(),
            "authors": entry.get("authors") or [],
            "year": entry.get("year"),
            "citations": (
                entry.get("cited_by")
                or entry.get("is_referenced_by_count")
                or 0
            ),
            "url": (
                entry.get("url")
                or entry.get("doi_url")
                or entry.get("link")
            )
        })

    # Sort and keep top 200
    cleaned = sorted(
        cleaned,
        key=lambda x: x["citations"] or 0,
        reverse=True
    )[:200]

    js_template = """
/**
 * ==========================================================
 * MOST CITED RESEARCH TABLE
 * ==========================================================
 *
 * HOW TO USE:
 *
 * 1. Include Tabulator:
 *    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
 *    <script src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>
 *
 * 2. Add this HTML:
 *
 *    <button id="download-csv">Download CSV</button>
 *    <div id="most-cited-research-table"></div>
 *
 * 3. Load this file AFTER Tabulator:
 *
 *    <script src="js/most_cited.js"></script>
 *
 * ==========================================================
 */

const mostCitedData = {data};

const table = new Tabulator("#most-cited-research-table", {{
    data: mostCitedData,
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 5,
    movableColumns: true,
    height: "700px",
    columns: [
        {{
            title: "Title",
            field: "title",
            headerFilter: "input",
            formatter: function(cell) {{
                const url = cell.getRow().getData().url;
                const val = cell.getValue();
                if (url) {{
                    return `<a href="${{url}}" target="_blank" rel="noopener noreferrer">${{val}}</a>`;
                }}
                return val;
            }}
        }},
        {{
            title: "Authors",
            field: "authors",
            headerFilter: "input",
            formatter: function(cell) {{
                const v = cell.getValue();
                return Array.isArray(v) ? v.join(", ") : v;
            }}
        }},
        {{
            title: "Year",
            field: "year",
            headerFilter: "input",
            width: 90
        }},
        {{
            title: "Citations",
            field: "citations",
            sorter: "number",
            headerFilter: "input",
            width: 120
        }}
    ]
}});

document.getElementById("download-csv").addEventListener("click", function () {{
    table.download("csv", "most_cited_research.csv");
}});
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_template.format(
            data=json.dumps(cleaned, indent=2)
        ))

    print(f"✔ Wrote {OUTPUT_FILE}")
    print(f"✔ Entries: {len(cleaned)}")


if __name__ == "__main__":
    build_js_table()
