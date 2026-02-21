#!/usr/bin/env python3
"""
Date: 2026-02-20

Objective:
    Query CrossRef for works matching ("Halophyte" AND "Halophile"),
    save paginated results, compile all pages, deduplicate by DOI,
    and generate a summary JSON after each page request.

Dependencies:
    Python 3.8+
    requests → pip install requests
"""

import os
import json
import time
import requests
from datetime import datetime


def query_crossref():
    """
    Main function to query CrossRef, save paginated results, and compile them.
    Saves summary JSON after each page request to track progress.
    """

    # -----------------------------
    # CONFIGURATION
    # -----------------------------
    query = '"Halophyte" AND "Halophile"'
    rows_per_page = 20
    max_pages = 1000

    pages_dir = "results/query/crossref/pages"
    summary_path = "results/query/crossref/query_crossref.json"

    os.makedirs(pages_dir, exist_ok=True)

    print("\n=== CrossRef Query Started ===")
    print("Pages directory:", os.path.abspath(pages_dir))
    print("Summary JSON path:", os.path.abspath(summary_path))

    # -----------------------------
    # PAGINATED QUERY
    # -----------------------------
    page = 0
    total_results = None

    while page < max_pages:
        offset = page * rows_per_page

        url = (
            "https://api.crossref.org/works"
            f"?query={query}"
            f"&rows={rows_per_page}"
            f"&offset={offset}"
        )

        print(f"\nRequesting page {page} (offset {offset})")

        try:
            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                print(f"⚠ Request blocked or failed (HTTP {response.status_code}). Continuing to next page.")
                break

            data = response.json()

            if total_results is None:
                total_results = data["message"]["total-results"]
                print(f"Total results reported by CrossRef: {total_results}")

            items = data["message"]["items"]

            if not items:
                print("No more results.")
                break

            # -----------------------------
            # SAVE PAGE WITH TIMESTAMP
            # -----------------------------
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            filename = f"{timestamp}_{page:04d}.json"
            filepath = os.path.join(pages_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
            print(f"Saved page → {os.path.abspath(filepath)}")

            # -----------------------------
            # COMPILE ALL PAGES AFTER EACH REQUEST
            # -----------------------------
            all_articles = []
            seen_dois = set()
            duplicates = 0

            for f_name in os.listdir(pages_dir):
                if not f_name.endswith(".json"):
                    continue
                f_path = os.path.join(pages_dir, f_name)
                with open(f_path, "r", encoding="utf-8") as f_page:
                    page_articles = json.load(f_page)

                for item in page_articles:
                    doi = item.get("DOI")
                    if doi:
                        doi = doi.lower().strip()

                    # Deduplicate by DOI
                    if doi and doi in seen_dois:
                        duplicates += 1
                        continue
                    if doi:
                        seen_dois.add(doi)

                    # Extract metadata of interest
                    authors = []
                    for a in item.get("author", []):
                        authors.append({
                            "given": a.get("given"),
                            "family": a.get("family"),
                            "affiliation": [aff.get("name") for aff in a.get("affiliation", [])]
                        })

                    funders = []
                    for fdr in item.get("funder", []):
                        funders.append({
                            "name": fdr.get("name"),
                            "award": fdr.get("award")
                        })

                    full_text_urls = [l.get("URL") for l in item.get("link", [])]

                    licenses = []
                    for lic in item.get("license", []):
                        licenses.append({
                            "url": lic.get("URL"),
                            "start_date": lic.get("start", {}).get("date-time")
                        })

                    article_dict = {
                        "doi": doi,
                        "doi_url": f"https://doi.org/{doi}" if doi else None,
                        "title": item.get("title"),
                        "publisher": item.get("publisher"),
                        "container_title": item.get("container-title"),
                        "content_type": item.get("type"),
                        "language": item.get("language"),
                        "abstract": item.get("abstract"),
                        "keywords": item.get("subject"),
                        "reference_count": item.get("reference-count"),
                        "is_referenced_by_count": item.get("is-referenced-by-count"),
                        "authors": authors,
                        "funders": funders,
                        "full_text_urls": full_text_urls,
                        "licenses": licenses
                    }

                    all_articles.append(article_dict)

            # -----------------------------
            # SUMMARY METRICS
            # -----------------------------
            article_count = len(all_articles)
            articles_found = len(seen_dois)
            articles_not_found = 0
            articles_not_list = []

            key_counts = {}
            for article in all_articles:
                for key, value in article.items():
                    if value not in (None, [], ""):
                        key_counts[key] = key_counts.get(key, 0) + 1

            keys_summary = []
            for key in sorted(key_counts.keys()):
                count = key_counts[key]
                percent = round((count / article_count) * 100, 2) if article_count else 0.0
                keys_summary.append({
                    "name": key,
                    "count": count,
                    "percent": percent
                })

            # Sort by citation count
            all_articles.sort(
                key=lambda x: x.get("is_referenced_by_count", 0) or 0,
                reverse=True
            )

            summary = {
                "article_count": article_count,
                "articles_found": articles_found,
                "articles_not_found": articles_not_found,
                "articles_not_list": articles_not_list,
                "keys": keys_summary,
                "duplicates": duplicates,
                "articles": all_articles
            }

            # -----------------------------
            # SAVE SUMMARY AFTER EACH PAGE
            # -----------------------------
            try:
                os.makedirs(os.path.dirname(summary_path), exist_ok=True)
                with open(summary_path, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)
                print(f"✅ Summary updated → {os.path.abspath(summary_path)}")
                print(f"Total articles compiled so far: {article_count}")
            except Exception as e:
                print(f"⚠ Failed to save summary: {e}")

            page += 1
            print("Waiting 5 seconds before next request...")
            time.sleep(5)

        except Exception as e:
            print(f"⚠ Error occurred: {e}")
            break

    print("\n=== CrossRef Query Complete ===")


if __name__ == "__main__":
    query_crossref()
