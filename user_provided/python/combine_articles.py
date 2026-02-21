#!/usr/bin/env python3
"""
Date: 2026-02-20

Objective:
    Combine CrossRef and Google Scholar articles into one deduplicated list,
    safely merge all metadata, and save a summarized JSON.

Dependencies:
    Python 3.8+
"""

import os
import json

def combine_articles():
    """
    Main function to combine CrossRef and Google Scholar articles.

    Workflow:
    1. Load CrossRef articles from openalex_crossref.json
    2. Load Google Scholar articles from openalex_gscholar.json
    3. Combine the 'articles' lists from both sources
    4. Deduplicate using DOI
    5. Merge metadata safely (handle dicts in lists)
    6. Count keys, duplicates, and other summary statistics
    7. Sort combined articles by most reliable citation count
    8. Save summary to compiled_articles.json
    """

    # -----------------------------
    # CONFIGURATION
    # -----------------------------
    crossref_path = "results/query/crossref/openalex_crossref.json"
    gscholar_path = "results/query/gscholar/openalex_gscholar.json"
    output_path = "results/query/compiled_articles.json"

    # -----------------------------
    # LOAD ARTICLES
    # -----------------------------
    print("Loading CrossRef articles...")
    with open(crossref_path, "r", encoding="utf-8") as f:
        crossref_data = json.load(f)
    crossref_articles = crossref_data.get("articles", [])
    print(f"Loaded {len(crossref_articles)} CrossRef articles.")

    print("Loading Google Scholar articles...")
    with open(gscholar_path, "r", encoding="utf-8") as f:
        gscholar_data = json.load(f)
    gscholar_articles = gscholar_data.get("articles", [])
    print(f"Loaded {len(gscholar_articles)} Google Scholar articles.")

    all_articles = crossref_articles + gscholar_articles
    print(f"Total articles before deduplication: {len(all_articles)}")

    # -----------------------------
    # DEDUPLICATE ARTICLES BY DOI
    # -----------------------------
    deduped_articles = []
    doi_map = {}
    duplicates = 0

    for article in all_articles:
        doi = article.get("doi")
        if doi:
            doi = doi.lower().strip()

        if doi and doi in doi_map:
            duplicates += 1
            existing = doi_map[doi]

            # Merge keys safely
            for k, value in article.items():
                if value is None:
                    continue

                if k not in existing:
                    existing[k] = value
                else:
                    # Merge lists safely
                    if isinstance(value, list) and isinstance(existing[k], list):
                        merged_list = []
                        seen = set()
                        for v in existing[k] + value:
                            if isinstance(v, dict):
                                # Serialize dicts to JSON string for deduplication
                                v_serial = json.dumps(v, sort_keys=True)
                                if v_serial not in seen:
                                    merged_list.append(v)
                                    seen.add(v_serial)
                            else:
                                if v not in seen:
                                    merged_list.append(v)
                                    seen.add(v)
                        existing[k] = merged_list
                    else:
                        # Prefer non-empty value
                        if not existing[k]:
                            existing[k] = value
            continue

        # New article
        if doi:
            doi_map[doi] = article
        deduped_articles.append(article)

    print(f"Total articles after deduplication: {len(deduped_articles)}")
    print(f"Duplicates merged: {duplicates}")

    # -----------------------------
    # SUMMARY METRICS
    # -----------------------------

    def citation_count(article):
        """
        Return a numeric citation count for sorting.
        Handles the case where 'is_referenced_by_count' or 'num_citations' is a list.
        """
        c = article.get("is_referenced_by_count")
        if isinstance(c, list):
            c = c[0] if c else 0
        if c is None:
            c = article.get("num_citations")
            if isinstance(c, list):
                c = c[0] if c else 0
        try:
            return int(c)
        except (TypeError, ValueError):
            return 0

    deduped_articles.sort(key=citation_count, reverse=True)

    key_counts = {}
    for article in deduped_articles:
        for key, value in article.items():
            if value not in (None, [], ""):
                key_counts[key] = key_counts.get(key, 0) + 1

    keys_summary = []
    total_articles = len(deduped_articles)
    for key in sorted(key_counts.keys()):
        count = key_counts[key]
        percent = round((count / total_articles) * 100, 2) if total_articles else 0.0
        keys_summary.append({
            "name": key,
            "count": count,
            "percent": percent
        })

    # Count articles with DOI
    articles_doi = sum(1 for a in deduped_articles if a.get("doi"))

    # Articles not found in either source
    articles_not_list = [
        a.get("doi") or a.get("title") for a in deduped_articles
        if not a.get("openalex") and not a.get("semanticscholar")
    ]

    summary = {
        "article_count": total_articles,
        "articles_doi": articles_doi,
        "articles_found_oa": sum(1 for a in deduped_articles if a.get("openalex")),
        "articles_found_ss": sum(1 for a in deduped_articles if a.get("semanticscholar")),
        "articles_not_found": len(articles_not_list),
        "articles_not_list": articles_not_list,
        "keys": keys_summary,
        "duplicates": duplicates,
        "articles": deduped_articles
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Combined summary saved → {output_path}")


if __name__ == "__main__":
    combine_articles()
