# date: 2026-02-23
# objective: Generate JS file for interactive article table with robust fallback for missing info
#            Initialize with most cited at the top and include Journal/Publisher column right after Title
# dependencies: json

import json

def table_articles():
    json_file = "results/query/compiled_articles.json"
    js_file = "docs/js/tableArticles.js"

    print("Loading JSON...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    print(f"Loaded {len(articles)} articles.")

    # -----------------------------
    # Helper functions
    # -----------------------------
    def safe_string(value):
        """Convert value to string, use first element if it's a list"""
        if isinstance(value, list):
            return str(value[0]) if value else "N/A"
        return str(value) if value is not None else "N/A"

    def get_nested(article, *keys):
        """Return nested value from dictionary safely"""
        current = article
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                current = current[key]
            else:
                current = None
                break
        return safe_string(current)

    def get_first_available(article, key_paths):
        """Try multiple paths in order, return first non-empty string or N/A"""
        for path in key_paths:
            value = get_nested(article, *path)
            if value != "N/A" and value != "":
                return value
        return "N/A"

    def resolve_url(article):
        url_paths = [
            ["doi_url"],
            ["pub_url"],
            ["link", 0, "URL"],
            ["openalex", "primary_location", "landing_page_url"],
        ]
        return get_first_available(article, url_paths)

    def resolve_citations(article):
        paths = [
            ["is-referenced-by-count"],
            ["num_citations"],
            ["openalex", "cited_by_count"]
        ]
        for path in paths:
            val = get_nested(article, *path)
            if str(val).isdigit() or isinstance(val, int):
                return int(val)
        return 0

    def resolve_type(article):
        paths = [
            ["container_type"],
            ["type"],
            ["bib", "type"],
            ["openalex", "type"]
        ]
        return get_first_available(article, paths)

    def resolve_journal_or_publisher(article):
        paths = [
            ["bib", "venue"],
            ["container-title", 0],
            ["publisher"],
            ["openalex", "primary_location", "source", "display_name"]
        ]
        return get_first_available(article, paths)

    # -----------------------------
    # Process articles
    # -----------------------------
    js_articles = []
    for article in articles:
        title = get_first_available(article, [
            ["bib", "title"],
            ["title"],
            ["openalex", "title"],
            ["openalex", "display_name"]
        ])
        year = get_first_available(article, [
            ["bib", "pub_year"],
            ["pub_year"],
            ["published-print", "date-parts", 0, 0],
            ["issued", "date-parts", 0, 0],
            ["openalex", "publication_year"]
        ])
        container_type = resolve_type(article)
        citations = resolve_citations(article)
        url = resolve_url(article)
        journal = resolve_journal_or_publisher(article)

        js_articles.append({
            "title": title,
            "url": url,
            "journal": journal,
            "type": container_type,
            "year": year,
            "citations": citations
        })

    # -----------------------------
    # Sort articles by citations descending
    # -----------------------------
    js_articles.sort(key=lambda x: x["citations"], reverse=True)

    # -----------------------------
    # Write JS
    # -----------------------------
    print("Writing JS table...")
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tableArticles.js\n")
        f.write("// Date: 2026-02-23\n\n")
        f.write("const articlesTableData = ")
        json.dump(js_articles, f, indent=2)
        f.write(";\n\n")

        f.write("document.addEventListener('DOMContentLoaded', function() {\n")
        f.write("  const articlesContainer = document.createElement('div');\n")
        f.write("  articlesContainer.id = 'articles-table-container';\n")
        f.write("  document.body.appendChild(articlesContainer);\n\n")
        f.write("  const articlesTitle = document.createElement('h2');\n")
        f.write("  articlesTitle.textContent = 'Articles Table';\n")
        f.write("  articlesContainer.appendChild(articlesTitle);\n\n")
        f.write("  const articlesDownloadBtn = document.createElement('button');\n")
        f.write("  articlesDownloadBtn.textContent = 'Download Table Data';\n")
        f.write("  articlesDownloadBtn.onclick = function() {\n")
        f.write("    articlesTable.download('csv', 'articles_table.csv');\n")
        f.write("  };\n")
        f.write("  articlesContainer.appendChild(articlesDownloadBtn);\n\n")
        f.write("  const articlesTableDiv = document.createElement('div');\n")
        f.write("  articlesTableDiv.id = 'articles-table';\n")
        f.write("  articlesContainer.appendChild(articlesTableDiv);\n\n")
        f.write("  const articlesTable = new Tabulator('#articles-table', {\n")
        f.write("    data: articlesTableData,\n")
        f.write("    layout: 'fitColumns',\n")
        f.write("    pagination: 'local',\n")
        f.write("    paginationSize: 20,\n")
        f.write("    initialSort:[\n")
        f.write("      {column:'citations', dir:'desc'}\n")
        f.write("    ],\n")
        f.write("    columns: [\n")
        f.write("      {\n")
        f.write("        title: 'Title', field: 'title', sorter: 'string', headerFilter: 'input',\n")
        f.write("        formatter: function(cell) {\n")
        f.write("          const value = cell.getValue();\n")
        f.write("          const url = cell.getRow().getData().url;\n")
        f.write("          return url && url !== 'N/A' ? `<a href='${url}' target='_blank'>${value}</a>` : value;\n")
        f.write("        }\n")
        f.write("      },\n")
        f.write("      { title: 'Journal/Publisher', field: 'journal', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Type', field: 'type', sorter: 'string', headerFilter: 'input' },\n")
        f.write("      { title: 'Year', field: 'year', sorter: 'number', headerFilter: 'input' },\n")
        f.write("      { title: 'Citations', field: 'citations', sorter: 'number', headerFilter: 'input' }\n")
        f.write("    ]\n")
        f.write("  });\n")
        f.write("});\n")

    print("✅ JS file with Journal/Publisher column moved successfully!")

if __name__ == "__main__":
    table_articles()
