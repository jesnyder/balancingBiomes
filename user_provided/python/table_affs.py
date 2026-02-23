# date: 2026-02-23
# objective: Generate a JavaScript file that builds an interactive Tabulator table
# showing unique affiliations with counts and geolocation status.
# Dependencies: json, built-in Python libraries only.
# This script reads 'compiled_affs.json' and outputs 'tableAffs.js'.
# The table is searchable, sortable, and allows CSV download.
# The div, data, and table variables all use the 'Affs' prefix.

import json

def table_affs():
    # Input and output file paths
    json_file = "results/query/compiled_affs.json"
    js_file = "docs/js/tableAffs.js"

    print("main running")
    print("Reading JSON data from", json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract counted affiliations
    affs_counted = data.get("affs_counted", [])
    print(f"Found {len(affs_counted)} counted affiliations")

    # Extract geolocated affiliations for 'found' check
    affs_geolocated = data.get("affs_geolocated", [])
    geolocated_names = {aff.get("name_original") for aff in affs_geolocated}
    print(f"Found {len(affs_geolocated)} geolocated affiliations")

    # Prepare JS-friendly data list
    AffsData = []
    for aff in affs_counted:
        name = aff.get("name", "")
        count = aff.get("count", 0)
        count_articles = aff.get("count_articles", 0)
        found = "Yes" if name in geolocated_names else "No"

        AffsData.append({
            "name": name,
            "count": count,
            "count_articles": count_articles,
            "found": found
        })

    # Sort descending by count
    AffsData.sort(key=lambda x: x["count"], reverse=True)
    print(f"Prepared {len(AffsData)} rows for the table, sorted by count descending")

    # Write JavaScript file
    print("Writing JavaScript file to", js_file)
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tableAffs.js\n")
        f.write("// Date: 2026-02-23\n")
        f.write("// Affiliation Table: columns = name, count, count_articles, found\n\n")

        # JS data
        f.write("const AffsData = ")
        json.dump(AffsData, f, indent=2)
        f.write(";\n\n")

        # JS code to build Tabulator table
        f.write("document.addEventListener('DOMContentLoaded', function() {\n")
        f.write("  const AffsDiv = document.createElement('div');\n")
        f.write("  AffsDiv.id = 'AffsDiv';\n")
        f.write("  AffsDiv.style.marginBottom = '50px';\n")
        f.write("  document.body.appendChild(AffsDiv);\n\n")

        f.write("  const titleAffs = document.createElement('h2');\n")
        f.write("  titleAffs.textContent = 'Affiliations Table';\n")
        f.write("  AffsDiv.appendChild(titleAffs);\n\n")

        f.write("  const downloadBtnAffs = document.createElement('button');\n")
        f.write("  downloadBtnAffs.textContent = 'Download Table Data';\n")
        f.write("  downloadBtnAffs.style.marginBottom = '10px';\n")
        f.write("  downloadBtnAffs.onclick = function() {\n")
        f.write("    AffsTable.download('csv', 'affiliations.csv');\n")
        f.write("  };\n")
        f.write("  AffsDiv.appendChild(downloadBtnAffs);\n\n")

        f.write("  const AffsTableDiv = document.createElement('div');\n")
        f.write("  AffsTableDiv.id = 'AffsTableDiv';\n")
        f.write("  AffsDiv.appendChild(AffsTableDiv);\n\n")

        f.write("  const AffsTable = new Tabulator('#AffsTableDiv', {\n")
        f.write("    data: AffsData,\n")
        f.write("    layout: 'fitColumns',\n")
        f.write("    pagination: 'local',\n")
        f.write("    paginationSize: 20,\n")
        f.write("    columns: [\n")
        f.write("      { title: 'Affiliation', field: 'name', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Count', field: 'count', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Count Articles', field: 'count_articles', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Found', field: 'found', sorter: 'string', headerFilter: 'input' },\n")
        f.write("    ]\n")
        f.write("  });\n")
        f.write("}); // end DOMContentLoaded\n")

    print("JS file successfully written with affiliation table!")

if __name__ == "__main__":
    table_affs()
