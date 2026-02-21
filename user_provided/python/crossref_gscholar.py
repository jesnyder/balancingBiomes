#!/usr/bin/env python3
"""
Date: 2026-02-19

Objective:
    Enrich Google Scholar articles with CrossRef metadata using DOI.

    Requirements implemented:
    ✔ Load Google Scholar results
    ✔ Deduplicate using DOI (without removing articles lacking DOI)
    ✔ Consolidate exact duplicates without DOI
    ✔ Query CrossRef using DOI
    ✔ Wait ≥5 seconds between requests
    ✔ Save progress after each article
    ✔ Maintain counts and sorted output
    ✔ Preserve all articles in final dataset

Dependencies:
    - Python 3.8+
    - requests
    - json
    - time
    - os
"""

import json
import time
import os
import requests


def crossref_gscholar():
    """Main function to enrich Google Scholar results with CrossRef metadata."""

    input_path = "results/query/gscholar/doi_gscholar.json"
    output_path = "results/query/gscholar/crossref_gscholar.json"

    print("\n[INFO] Starting CrossRef enrichment process...")

    # --------------------------------------------------
    # Load input file
    # --------------------------------------------------
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    print(f"[INFO] Articles loaded: {len(articles)}")

    # --------------------------------------------------
    # Deduplication
    # --------------------------------------------------
    print("[INFO] Deduplicating articles...")

    dedup_by_doi = {}
    no_doi_articles = []
    seen_no_doi = []

    for article in articles:
        doi = article.get("doi")

        # ------------------------------
        # Case 1: Article has DOI
        # ------------------------------
        if doi:
            if doi not in dedup_by_doi:
                dedup_by_doi[doi] = article.copy()
            else:
                existing = dedup_by_doi[doi]
                for key, value in article.items():
                    if key not in existing:
                        existing[key] = value
                    elif existing[key] != value:
                        if not isinstance(existing[key], list):
                            existing[key] = [existing[key]]
                        if value not in existing[key]:
                            existing[key].append(value)

        # ------------------------------
        # Case 2: Article WITHOUT DOI
        # Consolidate only exact duplicates
        # ------------------------------
        else:
            if article not in seen_no_doi:
                seen_no_doi.append(article)
                no_doi_articles.append(article)

    # Combine both groups
    articles = list(dedup_by_doi.values()) + no_doi_articles

    articles_with_doi = len(dedup_by_doi)
    articles_without_doi = len(no_doi_articles)

    print(f"[INFO] Articles with DOI: {articles_with_doi}")
    print(f"[INFO] Articles without DOI: {articles_without_doi}")
    print(f"[INFO] Total articles after deduplication: {len(articles)}")

    # --------------------------------------------------
    # Tracking variables
    # --------------------------------------------------
    missing_crossref = []
    keys_set = set()

    # --------------------------------------------------
    # Save progress helper
    # --------------------------------------------------
    def save_progress():
        """Save progress after each article."""

        def citation_count(article):
            return article.get("is-referenced-by-count", 0)

        sorted_articles = sorted(
            articles,
            key=citation_count,
            reverse=True
        )

        articles_count_2 = sum(
            1 for a in sorted_articles
            if a.get("is-referenced-by-count", 0) >= 2
        )

        output_data = {
            "articles_count": len(sorted_articles),
            "articles_count_2": articles_count_2,
            "articles_with_doi": articles_with_doi,
            "articles_without_doi": articles_without_doi,
            "keys": sorted(keys_set),
            "missing_crossref": sorted(missing_crossref),
            "articles": sorted_articles
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        print("[SAVE] Progress saved.")

    # --------------------------------------------------
    # CrossRef query function
    # --------------------------------------------------
    def fetch_crossref(doi):
        """Fetch metadata from CrossRef with required delay."""

        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            "User-Agent": "crossref-gscholar/1.0 (mailto:your_email@example.com)"
        }

        print("[WAIT] Waiting 5 seconds before request...")
        time.sleep(5)

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                return response.json().get("message", {})
            elif response.status_code == 404:
                print("[INFO] DOI not found in CrossRef.")
            else:
                print(f"[WARN] CrossRef returned status {response.status_code}")

        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")

        return None

    # --------------------------------------------------
    # Process articles
    # --------------------------------------------------
    for index, article in enumerate(articles, start=1):
        print(f"\n[PROCESS] Article {index}/{len(articles)}")

        doi = article.get("doi")

        # Skip CrossRef lookup if no DOI (but keep article)
        if not doi:
            print("[SKIP] No DOI → retained without CrossRef enrichment.")
            save_progress()
            continue

        print(f"[QUERY] CrossRef lookup for DOI: {doi}")
        metadata = fetch_crossref(doi)

        if metadata:
            print("[SUCCESS] Metadata retrieved.")
            for key, value in metadata.items():
                article[key] = value
                keys_set.add(key)
        else:
            print("[MISS] No CrossRef data returned.")
            missing_crossref.append(doi)

        save_progress()

    # --------------------------------------------------
    # Final save
    # --------------------------------------------------
    print("\n[FINAL] Finalizing counts and saving dataset...")
    save_progress()

    print("[COMPLETE] CrossRef enrichment finished.")


if __name__ == "__main__":
    crossref_gscholar()
