#!/usr/bin/env python3
"""
Date: 2026-02-20

Objective:
    Collect CrossRef metadata for a list of DOIs and produce a structured summary JSON.

    This script:
    • Reads DOIs from user_provided/admin/doi_included.csv
    • Cleans, normalizes, and deduplicates DOIs
    • Queries CrossRef API for metadata
    • Extracts specified metadata fields
    • Saves progress after each query
    • Generates a summary including key counts and percentages
    • Sorts articles by citation count (descending)

Dependencies:
    Python 3.8+
    requests → install with: pip install requests
"""

import os
import json
import time
import requests


def doi_crossref():
    """
    Main workflow for collecting CrossRef metadata.

    Designed for reliability and clarity:
    - Verbose progress messages
    - Graceful handling of missing metadata
    - Progress saved after each DOI query
    """

    input_path = "user_provided/admin/doi_included.csv"
    output_path = "results/query/crossref/doi_crossref.json"

    print("\n=== CrossRef DOI Metadata Collection Started ===")

    # -----------------------------
    # LOAD DOI LIST
    # -----------------------------
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found → {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        raw_dois = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(raw_dois)} DOIs from file.")

    # -----------------------------
    # CLEAN & DEDUPLICATE DOIs
    # -----------------------------
    cleaned_dois = [doi.lower().strip() for doi in raw_dois]
    unique_dois = list(dict.fromkeys(cleaned_dois))
    duplicates_count = len(cleaned_dois) - len(unique_dois)

    print(f"Unique DOIs: {len(unique_dois)}")
    print(f"Duplicates removed: {duplicates_count}")

    # -----------------------------
    # DATA STRUCTURES
    # -----------------------------
    articles = []
    articles_found = 0
    articles_not_found = 0
    articles_not_list = []
    key_counts = {}

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # -----------------------------
    # SAVE PROGRESS FUNCTION
    # -----------------------------
    def save_progress():
        """Save progress and summary JSON."""

        total_articles = len(unique_dois)

        keys_summary = []
        for key in sorted(key_counts.keys()):
            count = key_counts[key]
            percent = round((count / total_articles) * 100, 2) if total_articles else 0.0
            keys_summary.append({
                "name": key,
                "count": count,
                "percent": percent
            })

        summary = {
            "article_count": total_articles,
            "articles_found": articles_found,
            "articles_not_found": articles_not_found,
            "articles_not_list": articles_not_list,
            "keys": keys_summary,
            "duplicates": duplicates_count,
            "articles": articles
        }

        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(summary, out, indent=2)

        print("Progress saved.")

    # -----------------------------
    # QUERY CROSSREF
    # -----------------------------
    for idx, doi in enumerate(unique_dois, start=1):
        print(f"\nProcessing {idx}/{len(unique_dois)} → {doi}")

        url = f"https://api.crossref.org/works/{doi}"

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                message = response.json().get("message", {})

                # -----------------------------
                # AUTHORS
                # -----------------------------
                authors = []
                for a in message.get("author", []):
                    authors.append({
                        "given": a.get("given"),
                        "family": a.get("family"),
                        "affiliation": [aff.get("name") for aff in a.get("affiliation", [])]
                    })

                # -----------------------------
                # FUNDERS
                # -----------------------------
                funders = []
                for f in message.get("funder", []):
                    funders.append({
                        "name": f.get("name"),
                        "award": f.get("award")
                    })

                # -----------------------------
                # LINKS
                # -----------------------------
                full_text_urls = [l.get("URL") for l in message.get("link", [])]

                # -----------------------------
                # LICENSES
                # -----------------------------
                licenses = []
                for lic in message.get("license", []):
                    licenses.append({
                        "url": lic.get("URL"),
                        "start_date": lic.get("start", {}).get("date-time")
                    })

                # -----------------------------
                # ARTICLE METADATA
                # -----------------------------
                article_dict = {
                    "doi": doi,
                    "doi_url": f"https://doi.org/{doi}",
                    "title": message.get("title"),
                    "publisher": message.get("publisher"),
                    "container_title": message.get("container-title"),
                    "content_type": message.get("type"),
                    "language": message.get("language"),
                    "abstract": message.get("abstract"),
                    "keywords": message.get("subject"),
                    "reference_count": message.get("reference-count"),
                    "is_referenced_by_count": message.get("is-referenced-by-count"),
                    "authors": authors,
                    "funders": funders,
                    "full_text_urls": full_text_urls,
                    "licenses": licenses
                }

                articles_found += 1
                print("✓ Metadata found.")

            else:
                article_dict = {
                    "doi": doi,
                    "doi_url": f"https://doi.org/{doi}",
                    "error": f"HTTP {response.status_code}"
                }
                articles_not_found += 1
                articles_not_list.append(doi)
                print(f"✗ Metadata not found (HTTP {response.status_code}).")

        except Exception as e:
            article_dict = {
                "doi": doi,
                "doi_url": f"https://doi.org/{doi}",
                "error": str(e)
            }
            articles_not_found += 1
            articles_not_list.append(doi)
            print(f"✗ Error: {e}")

        # -----------------------------
        # TRACK KEYS
        # -----------------------------
        for key in article_dict.keys():
            key_counts[key] = key_counts.get(key, 0) + 1

        articles.append(article_dict)

        # Save after each DOI
        save_progress()

        # Respect CrossRef rate limits
        print("Waiting 5 seconds...")
        time.sleep(5)

    # -----------------------------
    # SORT BY CITATIONS
    # -----------------------------
    articles.sort(
        key=lambda x: x.get("is_referenced_by_count", 0) or 0,
        reverse=True
    )

    save_progress()

    print("\n=== Collection Complete ===")
    print(f"Results saved → {output_path}")


if __name__ == "__main__":
    doi_crossref()
