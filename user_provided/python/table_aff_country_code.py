# date: 2026-02-23
# objective: Generate a JavaScript file that builds an interactive Tabulator table
# showing unique affiliation country codes and their counts.
# The table is searchable, sortable, highest count at the top, download button included.
# Dependencies: json, Tabulator (JS library)
# All variable names use the "AffsCountryCode" suffix to prevent conflicts.

import json

def table_aff_country_code():
    """
    Main function to read geolocated affiliations JSON,
    count occurrences of each unique country code,
    and generate a JavaScript file to build an interactive Tabulator table.
    """

    # Define file paths
    json_file = "results/affs/geolocated_affs.json"
    js_file = "docs/js/tableAffsCountryCode.js"

    print("Reading JSON data from", json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    affs_geolocated = data.get("affs_geolocated", [])
    print(f"Found {len(affs_geolocated)} geolocated affiliations in JSON")

    # Count occurrences of each unique country code
    country_counts = {}
    for aff in affs_geolocated:
        country_code = aff.get("country_code", "").strip()
        country_name = aff.get("country_English", "").strip()
        if country_code:  # skip empty codes
            if country_code not in country_counts:
                country_counts[country_code] = {"country_code": country_code,
                                                "country_name": country_name,
                                                "count": 1}
            else:
                country_counts[country_code]["count"] += 1

    print(f"Found {len(country_counts)} unique country codes")

    # Convert to list and sort by count descending
    AffsCountryCodeData = list(country_counts.values())
    AffsCountryCodeData.sort(key=lambda x: x["count"], reverse=True)

    # Write the JS file
    print("Writing JavaScript file to", js_file)
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tableAffsCountryCode.js\n")
        f.write("// Date: 2026-02-23\n")
        f.write("// Table of unique affiliation country codes with counts\n")
        f.write("// Table is searchable, sortable, highest count at the top\n\n")

        # Write data variable
        f.write("const AffsCountryCodeData = ")
        json.dump(AffsCountryCodeData, f, indent=2)
        f.write(";\n\n")

        # Write DOMContentLoaded function to build the table
        f.write("document.addEventListener('DOMContentLoaded', function() {\n")
        f.write("  // Create container div\n")
        f.write("  const AffsCountryCodeDiv = document.createElement('div');\n")
        f.write("  AffsCountryCodeDiv.id = 'AffsCountryCodeDiv';\n")
        f.write("  AffsCountryCodeDiv.style.marginBottom = '50px';\n")
        f.write("  document.body.appendChild(AffsCountryCodeDiv);\n\n")

        f.write("  // Create title\n")
        f.write("  const titleAffsCountryCode = document.createElement('h2');\n")
        f.write("  titleAffsCountryCode.textContent = 'Affiliation Country Codes Table';\n")
        f.write("  AffsCountryCodeDiv.appendChild(titleAffsCountryCode);\n\n")

        f.write("  // Create download button\n")
        f.write("  const downloadBtnAffsCountryCode = document.createElement('button');\n")
        f.write("  downloadBtnAffsCountryCode.textContent = 'Download Table Data';\n")
        f.write("  downloadBtnAffsCountryCode.style.marginBottom = '10px';\n")
        f.write("  downloadBtnAffsCountryCode.onclick = function() {\n")
        f.write("    AffsCountryCodeTable.download('csv', 'affiliation_country_codes.csv');\n")
        f.write("  };\n")
        f.write("  AffsCountryCodeDiv.appendChild(downloadBtnAffsCountryCode);\n\n")

        f.write("  // Create table div\n")
        f.write("  const tableDivAffsCountryCode = document.createElement('div');\n")
        f.write("  tableDivAffsCountryCode.id = 'AffsCountryCodeTableDiv';\n")
        f.write("  AffsCountryCodeDiv.appendChild(tableDivAffsCountryCode);\n\n")

        f.write("  // Initialize Tabulator table\n")
        f.write("  const AffsCountryCodeTable = new Tabulator('#AffsCountryCodeTableDiv', {\n")
        f.write("    data: AffsCountryCodeData,\n")
        f.write("    layout: 'fitColumns',\n")
        f.write("    pagination: 'local',\n")
        f.write("    paginationSize: 20,\n")
        f.write("    initialSort: [{column:'count', dir:'desc'}], // sort by count descending\n")
        f.write("    columns: [\n")
        f.write("      { title: 'Country Code', field: 'country_code', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Country Name', field: 'country_name', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Count', field: 'count', sorter: 'number', headerFilter: 'input' }\n")
        f.write("    ]\n")
        f.write("  });\n")

        f.write("}); // end DOMContentLoaded\n")

    print("JS file successfully written with Tabulator table for affiliation country codes.")

if __name__ == "__main__":
    table_aff_country_code()
