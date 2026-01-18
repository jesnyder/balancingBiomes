# count_species.py
"""
Find Most Common Species in Halophyte/Halophile Research

Generates:
1. results/species_found/species_frequency.csv
2. results/species_found/species_frequency.json
3. docs/js/species_found.js (Tabulator table)
"""

import json
import pandas as pd
import os
from pathlib import Path

def count_species():
    print("Starting count_species...")

    # Paths
    species_json_file = Path("results/species_detailed.json")
    compiled_json_file = Path("results/search_results/list_compiled.json")
    output_dir = Path("results/species_found")
    output_dir.mkdir(parents=True, exist_ok=True)
    js_dir = Path("docs/js")
    js_dir.mkdir(parents=True, exist_ok=True)

    csv_output_file = output_dir / "species_frequency.csv"
    json_output_file = output_dir / "species_frequency.json"
    js_output_file = js_dir / "species_found.js"

    # Load species detailed JSON
    with open(species_json_file, encoding="utf-8") as f:
        species_data = json.load(f)

    print(f"Loaded {len(species_data)} species from {species_json_file}")

    # Build initial dataframe
    df_species = pd.DataFrame(species_data)
    if 'species_name' not in df_species.columns:
        # assume first key is the species name if different
        df_species.rename(columns={df_species.columns[0]: 'species_name'}, inplace=True)
    print("Initial species dataframe columns:", df_species.columns.tolist())

    # Load compiled articles
    with open(compiled_json_file, encoding="utf-8") as f:
        articles = json.load(f)

    total_articles = len(articles)
    print(f"Loaded {total_articles} articles from {compiled_json_file}")

    # Count articles with at least 2 citations
    def article_has_2_citations(article):
        cited_count = article.get("cited_by") or article.get("is_referenced_by_count") or 0
        return cited_count >= 2

    total_articles_2plus = sum(article_has_2_citations(a) for a in articles)
    print(f"Total articles with at least 2 citations: {total_articles_2plus}")

    # Initialize count columns
    counts = []
    counts_2plus = []

    # Fields to search in each article
    search_fields = ['title', 'abstract', 'keywords']
    print("Searching for species in article fields:", search_fields)

    for idx, row in df_species.iterrows():
        name = row['species_name']
        found_count = 0
        found_count_2plus = 0
        for article in articles:
            found_in_article = False
            for field in search_fields:
                content = article.get(field)
                if content and name.lower() in str(content).lower():
                    found_in_article = True
                    break
            if found_in_article:
                found_count += 1
                if article_has_2_citations(article):
                    found_count_2plus += 1
        counts.append(found_count)
        counts_2plus.append(found_count_2plus)
        print(f"[{idx+1}/{len(df_species)}] {name}: {found_count} articles, {found_count_2plus} with >=2 citations")

    # Add results to dataframe
    df_species['article_count'] = counts
    df_species['article_pct'] = df_species['article_count'] / total_articles * 100
    df_species['article_count_2plus'] = counts_2plus
    df_species['article_pct_2plus'] = df_species['article_count_2plus'] / total_articles_2plus * 100 if total_articles_2plus > 0 else 0

    # Sort by most frequent
    df_species.sort_values(by='article_count', ascending=False, inplace=True)

    # Save CSV and JSON
    df_species.to_csv(csv_output_file, index=False)
    df_species.to_json(json_output_file, orient='records', indent=2)
    print(f"Saved species frequency CSV: {csv_output_file}")
    print(f"Saved species frequency JSON: {json_output_file}")

    # Prepare JS file for Tabulator
    table_data = df_species.to_dict(orient='records')

    js_content = f"""
/*
Paste the following into index.html:
<link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
<div id="species_found"></div>
<script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
<script src="js/species_found.js"></script>

Notes:
- The div with id "species_found" will hold the table
- species_found.js must be loaded after Tabulator
*/

const speciesFound = {json.dumps(table_data, indent=2)};

const speciesTable = new Tabulator("#species_found", {{
    data: speciesFound,
    layout:"fitDataStretch",
    autoColumns:false,
    pagination:"local",
    paginationSize:20,
    columns:[
        {{title:"Species", field:"species_name"}},
        {{title:"Kingdom", field:"kingdom"}},
        {{title:"URL", field:"url", formatter:"link", formatterParams:{{target:"_blank"}}}},
        {{title:"Halotolerant", field:"halotolerant"}},
        {{title:"Articles Found", field:"article_count", hozAlign:"right", width:100}},
        {{title:"% of Articles", field:"article_pct", hozAlign:"right", width:100}},
        {{title:"Articles >=2 Citations", field:"article_count_2plus", hozAlign:"right", width:120}},
        {{title:"% Articles >=2 Citations", field:"article_pct_2plus", hozAlign:"right", width:120}}
    ],
    tooltips:true,
    movableColumns:true,
    resizableRows:true,
    paginationSizeSelector:[10, 20, 50, 100],
    placeholder:"No data available",
}});

// Add download button
const downloadBtn = document.createElement("button");
downloadBtn.innerText = "Download CSV";
downloadBtn.onclick = function() {{
    speciesTable.download("csv", "species_frequency.csv");
}};
document.getElementById("species_found").before(downloadBtn);
"""
    with open(js_output_file, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"Saved JS table file: {js_output_file}")


if __name__ == "__main__":
    count_species()
