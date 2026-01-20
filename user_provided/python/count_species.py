import json
from pathlib import Path


def count_species():
    print("🔍 Starting species frequency analysis...")

    # ----------------------------
    # Paths
    # ----------------------------
    SPECIES_FILE = Path("results/species_detailed.json")
    ARTICLES_FILE = Path("results/search_results/list_compiled.json")

    OUTPUT_JSON = Path("results/species_found/species_frequency.json")
    OUTPUT_JS_DIR = Path("docs/js")
    OUTPUT_JS = OUTPUT_JS_DIR / "species_found.js"

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JS_DIR.mkdir(parents=True, exist_ok=True)

    # ----------------------------
    # Load data
    # ----------------------------
    print("📖 Loading species list...")
    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    print("📖 Loading article list...")
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"✔ Loaded {len(species_list)} species")
    print(f"✔ Loaded {len(articles)} articles")

    # ----------------------------
    # Prepare article text blobs
    # ----------------------------
    article_texts = []
    articles_with_2plus_cites = 0

    for art in articles:
        citation_count = (
            art.get("cited_by")
            or art.get("is_referenced_by_count")
            or 0
        )

        if citation_count >= 2:
            articles_with_2plus_cites += 1

        combined = []
        for k, v in art.items():
            if k == "reference":
                continue
            if isinstance(v, str):
                combined.append(v)
            elif isinstance(v, list):
                combined.append(" ".join(str(x) for x in v))
            elif isinstance(v, dict):
                combined.append(" ".join(str(x) for x in v.values()))

        article_texts.append({
            "text": " ".join(combined).lower(),
            "citations": citation_count
        })

    print(f"✔ Articles with ≥2 citations: {articles_with_2plus_cites}")

    # ----------------------------
    # Count species mentions
    # ----------------------------
    results = []

    for entry in species_list:
        species_name = entry.get("species", "").strip()
        if not species_name:
            continue

        species_lower = species_name.lower()
        found_count = 0
        found_2plus = 0

        for art in article_texts:
            if species_lower in art["text"]:
                found_count += 1
                if art["citations"] >= 2:
                    found_2plus += 1

        if found_count == 0:
            continue

        total_articles = len(article_texts)

        result = dict(entry)  # preserve all original fields
        result["article_count"] = found_count
        result["article_pct"] = round((found_count / total_articles) * 100, 3)
        result["article_morethan2_count"] = found_2plus
        result["article_morethan2_pct"] = (
            round((found_2plus / articles_with_2plus_cites) * 100, 3)
            if articles_with_2plus_cites > 0 else 0.0
        )

        results.append(result)

    results.sort(key=lambda x: x["article_count"], reverse=True)

    # ----------------------------
    # Save JSON
    # ----------------------------
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✔ Saved JSON → {OUTPUT_JSON}")
    print(f"✔ Species found: {len(results)}")

    # ----------------------------
    # Build JS table
    # ----------------------------
    js_data = json.dumps(results, indent=2)

    js_template = f"""
/**
==========================================================
SPECIES FREQUENCY TABLE
==========================================================

HOW TO USE:

1. Add Tabulator:
<link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>

2. Add HTML:
<button id="download-species-csv">Download CSV</button>
<div id="species_found"></div>

3. Load this file after Tabulator:
<script src="js/species_found.js"></script>

==========================================================
*/

const speciesFound = {js_data};

const speciesTable = new Tabulator("#species_found", {{
    data: speciesFound,
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 20,
    movableColumns: true,
    height: "700px",

    columns: [
        {{ title: "Kingdom", field: "kingdom", headerFilter: "input" }},
        {{ title: "Phylum", field: "phylum", headerFilter: "input" }},
        {{ title: "Class", field: "class", headerFilter: "input" }},
        {{ title: "Order", field: "order", headerFilter: "input" }},
        {{ title: "Family", field: "family", headerFilter: "input" }},
        {{ title: "Species", field: "species", headerFilter: "input" }},
        {{
            title: "URL",
            field: "url",
            formatter: function(cell) {{
                const v = cell.getValue();
                if (!v) return "";
                return `<a href="${{v}}" target="_blank" rel="noopener noreferrer">link</a>`;
            }},
            width: "12%"
        }},
        {{ title: "Halotolerant", field: "halotolerant", headerFilter: "input", width: "10%" }},
        {{ title: "Article Count", field: "article_count", sorter: "number", width: "10%" }},
        {{ title: "Article %", field: "article_pct", sorter: "number", width: "10%" }},
        {{ title: "≥2 Cite Count", field: "article_morethan2_count", sorter: "number", width: "10%" }},
        {{ title: "≥2 Cite %", field: "article_morethan2_pct", sorter: "number", width: "10%" }}
    ]
}});

document.getElementById("download-species-csv").addEventListener("click", function () {{
    speciesTable.download("csv", "species_frequency.csv");
}});
"""

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_template)

    print(f"✔ JS table written → {OUTPUT_JS}")
    print("✅ Done.")


if __name__ == "__main__":
    count_species()
