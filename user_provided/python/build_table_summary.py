import pandas as pd
from pathlib import Path
import json

def build_table_summary():
    """
    Reads 'results/search_results/search_summary.csv' into a DataFrame
    and generates a JavaScript file 'docs/js/build_table_summary.js' that:
      - Hardcodes the table data
      - Uses Tabulator to display a sortable, searchable table
      - Adds column-level search inputs
      - Enables CSV download
      - Opens hyperlinks in a new tab
      - Displays all rows on one page
    """

    # -------------------------------
    # 1. Define paths
    # -------------------------------
    INPUT_CSV = Path("results/search_results/search_summary.csv")
    OUTPUT_DIR = Path("docs/js")
    OUTPUT_FILE = OUTPUT_DIR / "build_table_summary.js"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input CSV: {INPUT_CSV}")

    # -------------------------------
    # 2. Load CSV into a DataFrame
    # -------------------------------
    df = pd.read_csv(INPUT_CSV)

    # -------------------------------
    # 3. Convert DataFrame to list of dicts
    #    This list will be hardcoded in JS
    # -------------------------------
    data_list = df.to_dict(orient="records")
    data_json = json.dumps(data_list, indent=2)

    # -------------------------------
    # 4. JS template
    # -------------------------------
    js_template = f"""
/**
 * ==========================================================
 * SEARCH SUMMARY TABLE
 * ==========================================================
 *
 * INSTRUCTIONS:
 *
 * 1. Include Tabulator CSS and JS in your index.html (in <head> or before </body>):
 *    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
 *    <script src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>
 *
 * 2. Add this HTML in your index.html body where you want the table:
 *    <button id="download-table-data">Download Table Data</button>
 *    <div id="table_search_summary"></div>
 *
 * 3. Load this JS file AFTER the div/button:
 *    <script src="js/build_table_summary.js"></script>
 *
 * WHY:
 * - Data is hardcoded to allow client-side rendering without backend.
 * - Tabulator provides dynamic sorting, filtering, and CSV export.
 * - Column header filters allow searching each column individually.
 * - Hyperlinks in the table will open safely in a new tab.
 * - Pagination is set to display all rows so the full table is visible.
 *
 * ==========================================================
 */

 // -------------------------------
 // 4a. Hardcoded table data
 // -------------------------------
const table_summary_data = {data_json};

 // -------------------------------
 // 4b. Create Tabulator table
 // -------------------------------
const table_search_summary = new Tabulator("#table_search_summary", {{
    data: table_summary_data,           // Load the hardcoded data
    layout: "fitColumns",               // Adjust columns to fit the table width
    pagination: "local",                // Enable pagination
    paginationSize: table_summary_data.length, // Show all rows on one page
    movableColumns: true,               // Allow columns to be reordered
    height: "600px",                    // Fixed height with scroll if needed
    columns: Object.keys(table_summary_data[0] || {{}}).map(key => {{
        return {{
            // Convert column keys to human-readable titles
            title: key.replace(/_/g, " ").replace(/\\b\\w/g, l => l.toUpperCase()),
            field: key,
            headerFilter: "input",      // Adds a search input below the header
            formatter: function(cell) {{
                // Detect if value looks like a URL and render as hyperlink
                const val = cell.getValue();
                const urlPattern = /^https?:\\/\\//i;
                if (val && typeof val === "string" && urlPattern.test(val)) {{
                    return `<a href="${{val}}" target="_blank" rel="noopener noreferrer">${{val}}</a>`;
                }}
                return val;
            }}
        }};
    }})
}});

 // -------------------------------
 // 4c. Add CSV download functionality
 // -------------------------------
document.getElementById("download-table-data").addEventListener("click", function() {{
    table_search_summary.download("csv", "search_summary_table.csv");
}});
"""

    # -------------------------------
    # 5. Write JS file
    # -------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_template)

    print(f"✔ Wrote JS file: {OUTPUT_FILE}")
    print(f"✔ Columns: {list(df.columns)}")
    print(f"✔ Rows: {len(df)}")


# -------------------------------
# Run main function if called directly
# -------------------------------
if __name__ == "__main__":
    build_table_summary()
