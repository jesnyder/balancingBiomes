# =========================================================
# Date prepared: 2026-01-31
# Objective: Compile, clean, deduplicate, enrich with DOI,
#            and save Google Scholar results as enriched JSON.
# Tasks:
#   1. Read all JSON files from results/search_results/gscholar/pages.
#      - Supports both list-of-articles or {"results": [...]} formats.
#   2. Combine all articles into a single list.
#   3. Remove existing 'doi' and 'doi_url' keys.
#   4. Deduplicate articles (title + authors + year).
#   5. Clean HTML tags and remove test labels like [PDF], [BOOK] from title/snippet.
#   6. Add 'doi' and 'doi_url' by extracting DOI from pub_url using regex rules.
#   7. Deduplicate again using DOI.
#   8. Sort by number of citations (descending).
#   9. Save enriched JSON with summary counts and list of keys.
# Input:
#   - JSON files in results/search_results/gscholar/pages/
# Output:
#   - JSON file: results/search_results/enriched/enriched_gscholar.json
# =========================================================

import os
import json
import re
from bs4 import BeautifulSoup

def enrich_gscholar():
    print("📂 Starting Google Scholar enrichment...")

    # -------------------------------
    # Directories and output file
    # -------------------------------
    INPUT_DIR = "results/search_results/gscholar/pages"
    OUTPUT_FILE = "results/search_results/enriched/enriched_gscholar.json"
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # -------------------------------
    # DOI regex pattern
    # -------------------------------
    DOI_PATTERN = re.compile(r'10\.\d{4,9}/[\w\.-]+')

    # -------------------------------
    # Step 1: Read all JSON files
    # -------------------------------
    json_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".json")])
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in: {INPUT_DIR}")

    articles_all = []
    print(f"Found {len(json_files)} JSON files, reading...")

    for fname in json_files:
        fpath = os.path.join(INPUT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not parse {fname}: {e}")
                continue

            if isinstance(data, list):
                articles_all.extend(data)
            elif isinstance(data, dict) and "results" in data:
                articles_all.extend(data["results"])
            else:
                print(f"⚠️ Warning: Unrecognized JSON structure in {fname}")

    print(f"Total articles before cleaning: {len(articles_all)}")

    # -------------------------------
    # Step 2: Remove existing DOI info
    # -------------------------------
    for art in articles_all:
        art.pop("doi", None)
        art.pop("doi_url", None)

    # -------------------------------
    # Step 3: Deduplicate by title + authors + year
    # -------------------------------
    seen = set()
    deduped_articles = []
    for art in articles_all:
        key = (art.get("title","").strip().lower(), tuple(art.get("authors",[])), art.get("year",""))
        if key not in seen:
            deduped_articles.append(art)
            seen.add(key)

    print(f"Total articles after first deduplication: {len(deduped_articles)}")

    # -------------------------------
    # Step 4: Clean HTML and remove labels
    # -------------------------------
    for art in deduped_articles:
        for field in ["title", "snippet"]:
            if field in art and art[field]:
                # Remove HTML tags
                art[field] = BeautifulSoup(art[field], "html.parser").get_text()
                # Remove labels like [PDF], [BOOK], [HTML], [B]
                art[field] = re.sub(r"\[(PDF|BOOK|HTML|B)\]", "", art[field], flags=re.IGNORECASE).strip()

    # -------------------------------
    # Step 5: Initialize DOI fields
    # -------------------------------
    for art in deduped_articles:
        art["doi"] = ""
        art["doi_url"] = ""

        # Search for DOI in pub_url
        pub_url = art.get("pub_url", "")
        if pub_url:
            match = DOI_PATTERN.search(pub_url)
            if match:
                doi_found = match.group(0)
                art["doi"] = doi_found
                art["doi_url"] = f"https://doi.org/{doi_found}"

    # -------------------------------
    # Step 6: Deduplicate again using DOI
    # -------------------------------
    seen_doi = set()
    final_articles = []
    for art in deduped_articles:
        doi_key = art["doi"] if art["doi"] else art.get("title","").strip().lower()
        if doi_key not in seen_doi:
            final_articles.append(art)
            seen_doi.add(doi_key)

    # -------------------------------
    # Step 7: Sort by citations (most cited first)
    # -------------------------------
    final_articles.sort(key=lambda x: x.get("num_citations", x.get("citations", 0)), reverse=True)

    # -------------------------------
    # Step 8: Collect statistics
    # -------------------------------
    count_abstract = sum(1 for art in final_articles if art.get("abstract"))
    count_doi = sum(1 for art in final_articles if art.get("doi"))
    count_2 = sum(1 for art in final_articles if art.get("num_citations", art.get("citations",0)) >= 2)
    keys = list({k for art in final_articles for k in art.keys()})

    enriched_data = {
        "database": "gscholar",
        "count": len(final_articles),
        "count_abstract": count_abstract,
        "count_doi": count_doi,
        "count_2": count_2,
        "keys": keys,
        "articles": final_articles
    }

    # -------------------------------
    # Step 9: Save enriched JSON
    # -------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Google Scholar enrichment complete. Saved to: {OUTPUT_FILE}")
    print(f"Total articles: {len(final_articles)}, with abstract: {count_abstract}, with DOI: {count_doi}")


# Run standalone
if __name__ == "__main__":
    enrich_gscholar()
