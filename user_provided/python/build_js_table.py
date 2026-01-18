# build_js_table.py
"""
This script builds a JavaScript file that renders a table of the 200 most cited
articles from results/search_results/list_compiled.json using Tabulator.

Instructions for index.html:
1. Include Tabulator CSS and JS in your HTML head:
   <link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
   <script type="text/javascript" src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>

2. Include the generated JS file before the closing </body>:
   <script src="js/most_cited.js"></script>

3. Add a div for the table:
   <div id="most-cited-research-table"></div>
"""

import json
import os

def build_js_table():
    input_json_path = "results/search_results/list_compiled.json"
    output_js_path = "docs/js/most_cited.js"

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_js_path), exist_ok=True)

    print("Loading JSON data...")
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Use cited_by or is_referenced_by_count for ranking
    def get_citations(entry):
        return entry.get("cited_by") or entry.get("is_referenced_by_count") or 0

    print("Sorting articles by citation count...")
    data_sorted = sorted(data, key=get_citations, reverse=True)[:200]

    # Prepare JS data variable
    print(f"Preparing JS variable with {len(data_sorted)} articles...")
    js_data_var = "mostCitedData"
    js_data = f"const {js_data_var} = {json.dumps(data_sorted, indent=2)};\n\n"

    # Prepare JS for Tabulator
    js_tabulator = f"""
// Create Tabulator table for most cited research
const mostCitedTable = new Tabulator("#most-cited-research-table", {{
    data: {js_data_var},
    layout: "fitDataStretch",
    responsiveLayout: "hide",
    pagination: "local",
    paginationSize: 20,
    columns: [
        {{title: "Title", field: "title", headerFilter: "input", formatter: function(cell, formatterParams, onRendered) {{
            const val = cell.getValue();
            const url = cell.getData().url;
            return url ? `<a href='${{url}}' target='_blank'>${{val}}</a>` : val;
        }}}},
        {{title: "Authors", field: "authors", headerFilter: "input"}},
        {{title: "Year", field: "year", headerFilter: "input"}},
        {{title: "Citations", field: "cited_by", hozAlign: "right", width: 80, sorter: "number"}}
    ],
}});

// Add download button
const downloadButton = document.createElement("button");
downloadButton.innerText = "Download CSV";
downloadButton.onclick = function() {{
    mostCitedTable.download("csv", "most_cited_research.csv");
}};
const container = document.getElementById("most-cited-research-table");
container.parentNode.insertBefore(downloadButton, container);
"""

    print(f"Writing JS to {output_js_path}...")
    with open(output_js_path, "w", encoding="utf-8") as f:
        f.write(js_data)
        f.write(js_tabulator)

    print("Done! JavaScript table created.")

# If running as main script
if __name__ == "__main__":
    build_js_table()
