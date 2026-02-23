# date: 2026-02-23
# objective: Generate a JavaScript file that builds an interactive Tabulator table
# showing organism counts from count_organisms.json.
# Synonyms column after GBIF URL, Phylum after Kingdom.
# Table is searchable, sortable, GBIF URLs open in a new tab, download button included.
# Pagination added: 20 rows per page.

import json

def table_organisms():
    # File paths
    json_file = "results/counts/count_organisms.json"
    js_file = "docs/js/tableCounts.js"

    print("Reading JSON data from", json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    organisms = data.get("organisms", [])
    print(f"Found {len(organisms)} organisms in JSON")

    # Prepare JS-friendly data
    js_organisms_list = []
    for org in organisms:
        js_organisms_list.append({
            "queryName": org.get("queryName", ""),
            "gbif_url": org.get("gbif_url", ""),
            "synonyms": ", ".join(org.get("synonyms", [])),
            "kingdom": org.get("kingdom", ""),
            "phylum": org.get("phylum", ""),
            "count": org.get("count", 0),
            "count_2": org.get("count_2", 0)
        })

    # Write JS file
    print("Writing JS file to", js_file)
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tableCounts.js\n")
        f.write("// Date: 2026-02-23\n")
        f.write("// Organism Counts Table: synonyms after GBIF URL, Phylum after Kingdom\n")
        f.write("// Pagination: 20 rows per page\n\n")

        f.write("const organismsDataCounts = ")
        json.dump(js_organisms_list, f, indent=2)
        f.write(";\n\n")

        f.write("document.addEventListener('DOMContentLoaded', function() {\n")
        f.write("  const containerCounts = document.createElement('div');\n")
        f.write("  containerCounts.id = 'organisms-table-container';\n")
        f.write("  containerCounts.style.marginBottom = '50px';\n")
        f.write("  document.body.appendChild(containerCounts);\n\n")

        f.write("  const titleCounts = document.createElement('h2');\n")
        f.write("  titleCounts.textContent = 'Organism Counts Table';\n")
        f.write("  containerCounts.appendChild(titleCounts);\n\n")

        f.write("  const downloadBtnCounts = document.createElement('button');\n")
        f.write("  downloadBtnCounts.textContent = 'Download Table Data';\n")
        f.write("  downloadBtnCounts.style.marginBottom = '10px';\n")
        f.write("  downloadBtnCounts.onclick = function() {\n")
        f.write("    organismsTableCounts.download('csv', 'organism_counts.csv');\n")
        f.write("  };\n")
        f.write("  containerCounts.appendChild(downloadBtnCounts);\n\n")

        f.write("  const tableDivCounts = document.createElement('div');\n")
        f.write("  tableDivCounts.id = 'organisms-table';\n")
        f.write("  containerCounts.appendChild(tableDivCounts);\n\n")

        f.write("  const organismsTableCounts = new Tabulator('#organisms-table', {\n")
        f.write("    data: organismsDataCounts,\n")
        f.write("    layout: 'fitColumns',\n")
        f.write("    pagination: 'local',\n")
        f.write("    paginationSize: 20,\n")  # 20 rows per page
        f.write("    columns: [\n")
        f.write("      { title: 'Organism', field: 'queryName', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'GBIF Url', field: 'gbif_url', formatter:'link', formatterParams:{ target:'_blank' }, headerFilter:'input' },\n")
        f.write("      { title: 'Synonyms', field: 'synonyms', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Kingdom', field: 'kingdom', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Phylum', field: 'phylum', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Count', field: 'count', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Count More than 2', field: 'count_2', sorter: 'number', headerFilter: 'input' },\n")
        f.write("    ]\n")
        f.write("  });\n")
        f.write("}); // end DOMContentLoaded\n")

    print("JS file successfully written with pagination enabled!")

if __name__ == "__main__":
    table_organisms()
