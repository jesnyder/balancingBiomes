#!/usr/bin/env python3
"""
Date: 2026-02-22

Objective:
    Build an index.html file that displays all Tabulator tables defined in JS files
    in docs/js. Automatically detects table variable names and creates div containers.

Dependencies:
    - os
    - re
"""

import os
import re

def write_html():
    """Generate docs/index.html to display all Tabulator tables in docs/js."""

    js_dir = "docs/js"
    output_html = "docs/index.html"

    print("Scanning JS files for tables...")

    # List all JS files in the js_dir
    js_files = [f for f in os.listdir(js_dir) if f.endswith(".js")]

    table_vars = []

    # Regex to detect Tabulator initialization: new Tabulator(...)
    tabulator_regex = re.compile(r'new\s+Tabulator\s*\(\s*(\w+)')

    for js_file in js_files:
        path = os.path.join(js_dir, js_file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            matches = tabulator_regex.findall(content)
            table_vars.extend(matches)

    table_vars = sorted(set(table_vars))
    print(f"Found {len(table_vars)} table variables: {table_vars}")

    # Build HTML
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "  <title>Balancing Biomes Tables</title>",
        "  <!-- Tabulator CSS -->",
        "  <link href='https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css' rel='stylesheet'>",
        "  <style>",
        "    body { font-family: Arial, sans-serif; padding: 20px; }",
        "    .table-container { margin-bottom: 50px; }",
        "    .table-title { font-size: 1.5em; margin-bottom: 10px; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>Balancing Biomes Tables</h1>"
    ]

    # Add a div for each table
    for var in table_vars:
        html_lines.append("  <div class='table-container'>")
        html_lines.append(f"    <div class='table-title'>{var}</div>")
        html_lines.append(f"    <div id='{var}'></div>")
        html_lines.append("  </div>")

    # Include Tabulator JS and the user JS files
    html_lines.append("  <!-- Tabulator JS -->")
    html_lines.append("  <script src='https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js'></script>")

    for js_file in js_files:
        html_lines.append(f"  <script src='js/{js_file}'></script>")

    html_lines.append("</body>")
    html_lines.append("</html>")

    # Write HTML
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"HTML file generated → {output_html}")


if __name__ == "__main__":
    write_html()
