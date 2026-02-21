"""
Date: 2026-02-19
Objective:
    Enrich compiled Google Scholar results by extracting DOIs from article URLs.
    The script scans article URLs, detects DOI substrings, trims them using an
    exclusion list, normalizes them, and adds `doi` and `doi_url` fields.

Dependencies:
    - Python 3.x (standard library only)
    - Input file:
        results/query/gscholar/query_gscholar.json
    - DOI exclusion list:
        user_provided/admin/doi_excluded.csv
        (one string per line, no header)
    - Output file:
        results/query/gscholar/doi_gscholar.json
"""

import json
import os
import re


def doi_gscholar():
    print("\n=== DOI ENRICHMENT STARTED ===\n")

    # -----------------------------
    # FILE PATHS
    # -----------------------------
    input_file = "results/query/gscholar/query_gscholar.json"
    output_file = "results/query/gscholar/doi_gscholar.json"
    exclusion_file = "user_provided/admin/doi_excluded.csv"

    # -----------------------------
    # STEP 1: LOAD DOI EXCLUSION LIST
    # -----------------------------
    print("Loading DOI exclusion list...")

    doi_exclusions = []

    if os.path.exists(exclusion_file):
        with open(exclusion_file, "r", encoding="utf-8") as f:
            # Each line = phrase indicating DOI termination
            doi_exclusions = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(doi_exclusions)} exclusion patterns.")

    # -----------------------------
    # STEP 2: LOAD COMPILED RESULTS
    # -----------------------------
    print("\nLoading compiled Google Scholar results...")

    if not os.path.exists(input_file):
        print("ERROR: Input file not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    print(f"Loaded {len(articles)} articles.")

    # -----------------------------
    # STEP 3: DOI PATTERN
    # -----------------------------
    """
    DOI pattern based on specification:

    - Starts with 10.
    - Publisher number
    - Slash separator
    - Allowed characters:
        letters, numbers, . - _ / ( ) : ;

    No spaces allowed.
    """

    doi_pattern = re.compile(r"10\.\d+/[A-Za-z0-9.\-_/():;]+")

    # -----------------------------
    # STEP 4: PROCESS ARTICLES
    # -----------------------------
    print("\nScanning articles for DOIs...\n")

    doi_urls = []  # collect doi_url values for longest list

    for idx, article in enumerate(articles, start=1):
        print(f"Processing article {idx}/{len(articles)}")

        doi_found = None

        # Search priority keys
        for key in ["pub_url", "eprint_url"]:
            url = article.get(key)
            if not url:
                continue

            match = doi_pattern.search(url)
            if match:
                doi_found = match.group(0)
                print(f"  DOI candidate found in {key}: {doi_found}")
                break

        # -----------------------------
        # CLEAN DOI USING EXCLUSION LIST
        # -----------------------------
        if doi_found:
            for exclusion in doi_exclusions:
                if exclusion in doi_found:
                    print(f"  Trimming DOI at exclusion pattern: {exclusion}")
                    doi_found = doi_found.split(exclusion)[0]

            # Normalize case (DOIs are case-insensitive)
            doi_found = doi_found.lower()

            # Construct DOI URL
            doi_url = f"https://doi.org/{doi_found}"

            # Add to article
            article["doi"] = doi_found
            article["doi_url"] = doi_url

            doi_urls.append(doi_url)

            print(f"  Final DOI: {doi_found}")
        else:
            print("  No DOI found.")

    # -----------------------------
    # STEP 5: LIST 10 LONGEST DOI_URL VALUES
    # -----------------------------
    print("\nTop 10 longest doi_url values:\n")

    longest = sorted(doi_urls, key=len, reverse=True)[:10]

    for url in longest:
        print(f"{url}  (length: {len(url)})")

    # -----------------------------
    # STEP 6: SAVE ENRICHED RESULTS
    # -----------------------------
    print("\nSaving enriched results...")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    output_data = {
        "article_count": len(articles),
        "article_count_2": data.get("article_count_2", 0),
        "articles": articles,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_file}")
    print("\n=== DOI ENRICHMENT COMPLETE ===\n")
