# date: 2026-02-23
# objective: Generate a JavaScript file that builds an interactive Tabulator table
# showing affiliations from compiled and geolocated JSON files.
# Columns: Name, Count, Count Articles, Found (Yes/No if geolocated)
# Table is searchable, sortable, download button included, pagination 20 rows per page.

import json

def table_affs():
    print("main running")

    # File paths
    counted_file = "results/query/compiled_affs.json"
    geolocated_file = "results/affs/geolocated_affs.json"
    js_file = "docs/js/tableAffs.js"

    # Open counted affiliations
    print(f"Opening counted affiliations: {counted_file}")
    with open(counted_file, "r", encoding="utf-8") as f:
        compiled_data = json.load(f)
    affs_counted = compiled_data.get("affs_counted", [])
    print(f"Number of counted affiliations found: {len(affs_counted)}")
    if len(affs_counted) > 0:
        print("First 3 counted affiliations:", affs_counted[:3])

    # Open geolocated affiliations
    print(f"Opening geolocated affiliations: {geolocated_file}")
    with open(geolocated_file, "r", encoding="utf-8") as f:
        geoloc_data = json.load(f)
    affs_geolocated = geoloc_data.get("affs_geolocated", [])
    print(f"Number of geolocated affiliations found: {len(affs_geolocated)}")
    if len(affs_geolocated) > 0:
        print("First 3 geolocated affiliations:", affs_geolocated[:3])

    # Make a set of geolocated names for fast lookup
    geolocated_names = {aff.get("name_original", "").strip() for aff in affs_geolocated}
    print(f"Number of unique geolocated names collected: {len(geolocated_names)}")

    # Prepare data for JS table
    rows = []
    for aff in affs_counted:
        name_clean = aff.get("name", "").strip()
        rows.append({
            "name": name_clean,
            "count": aff.get("count", 0),
            "count_articles": aff.get("count_articles", 0),
            "found": "Yes" if name_clean in geolocated_names else "No"
        })
    # Sort descending by count
    rows.sort(key=lambda x: x["count"], reverse=True)
    print(f"Prepared {len(rows)} rows for the table, sorted by count descending")

    # Write JS file
    print(f"Writing JavaScript file to {js_file}")
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tableAffs.js\n")
        f.write("// Date: 2026-02-23\n")
        f.write("// Affiliations Table: includes 'found' column\n")
        f.write("// Sorted by count descending, searchable and sortable\n\n")

        f.write("const AffsData = ")
        json.dump(rows, f, indent=2)
        f.write(";\n\n")

        f.write("document.addEventListener('DOMContentLoaded', function() {\n")
        f.write("  const AffsDiv = document.createElement('div');\n")
        f.write("  AffsDiv.id = 'AffsDiv';\n")
        f.write("  AffsDiv.style.marginBottom = '50px';\n")
        f.write("  document.body.appendChild(AffsDiv);\n\n")

        f.write("  const titleAffs = document.createElement('h2');\n")
        f.write("  titleAffs.textContent = 'Affiliation Counts Table';\n")
        f.write("  AffsDiv.appendChild(titleAffs);\n\n")

        f.write("  const downloadBtnAffs = document.createElement('button');\n")
        f.write("  downloadBtnAffs.textContent = 'Download Table Data';\n")
        f.write("  downloadBtnAffs.style.marginBottom = '10px';\n")
        f.write("  downloadBtnAffs.onclick = function() {\n")
        f.write("    AffsTable.download('csv', 'affiliations.csv');\n")
        f.write("  };\n")
        f.write("  AffsDiv.appendChild(downloadBtnAffs);\n\n")

        f.write("  const tableDivAffs = document.createElement('div');\n")
        f.write("  tableDivAffs.id = 'AffsTableDiv';\n")
        f.write("  AffsDiv.appendChild(tableDivAffs);\n\n")

        f.write("  const AffsTable = new Tabulator('#AffsTableDiv', {\n")
        f.write("    data: AffsData,\n")
        f.write("    layout: 'fitColumns',\n")
        f.write("    pagination: 'local',\n")
        f.write("    paginationSize: 20,\n")
        f.write("    columns: [\n")
        f.write("      { title: 'Name', field: 'name', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Count', field: 'count', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Count Articles', field: 'count_articles', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Found', field: 'found', sorter: 'string', headerFilter: 'input' },\n")
        f.write("    ]\n")
        f.write("  });\n")
        f.write("}); // end DOMContentLoaded\n")

    print("JS file successfully written with affiliation table!")

if __name__ == "__main__":
    table_affs()
