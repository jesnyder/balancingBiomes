#!/usr/bin/env python3
"""
Date: 2026-02-22

Objective:
    Extract, count, and summarize all affiliations from compiled articles.

Dependencies:
    Python 3.8+
"""

import os
import json
from collections import Counter, defaultdict

def list_affs():
    """
    Extract affiliations from compiled articles and summarize results.

    This function is designed to be robust against real-world metadata issues:
    - affiliation may be None
    - affiliation may be a string or list
    - authors may be strings instead of dictionaries
    - missing keys are handled safely
    """

    # -----------------------------
    # CONFIGURATION
    # -----------------------------
    input_path = "results/query/compiled_articles.json"
    output_path = "results/query/compiled_affs.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # -----------------------------
    # LOAD COMPILED ARTICLES
    # -----------------------------
    print("\n=== Loading compiled articles ===")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    total_articles = len(articles)

    print(f"Total articles loaded: {total_articles}")

    # -----------------------------
    # INITIALIZE COUNTERS
    # -----------------------------
    all_affs = []                       # every affiliation instance
    affs_article_counter = defaultdict(int)  # counts per unique article
    articles_with_affs_count = 0

    # -----------------------------
    # PROCESS ARTICLES
    # -----------------------------
    for idx, article in enumerate(articles, start=1):
        article_has_aff = False
        unique_article_affs = set()

        authors = article.get("authors", [])

        for author in authors:
            # Some entries are strings instead of dicts → skip safely
            if not isinstance(author, dict):
                continue

            affs = author.get("affiliation")

            # Normalize affiliation field into a list
            if affs is None:
                continue
            elif isinstance(affs, str):
                affs = [affs]
            elif not isinstance(affs, list):
                continue

            for aff in affs:
                # Skip non-string or empty values safely
                if not isinstance(aff, str):
                    continue

                aff = aff.strip()

                if not aff:
                    continue

                # Track counts
                all_affs.append(aff)
                unique_article_affs.add(aff)
                article_has_aff = True

        # Count each unique affiliation per article (no double counting)
        for aff in unique_article_affs:
            affs_article_counter[aff] += 1

        if article_has_aff:
            articles_with_affs_count += 1

        # Progress reporting
        if idx % 100 == 0 or idx == total_articles:
            print(f"Processed {idx}/{total_articles} articles...")

    # -----------------------------
    # SUMMARIZE AFFILIATIONS
    # -----------------------------
    aff_counts_total = Counter(all_affs)
    unique_affs = sorted(aff_counts_total.keys())

    most_common_affs = [name for name, _ in aff_counts_total.most_common(10)]

    affs_counted = []
    for aff in unique_affs:
        affs_counted.append({
            "name": aff,
            "count": aff_counts_total[aff],
            "count_articles": affs_article_counter.get(aff, 0)
        })

    # Sort so most cited affiliations appear first
    affs_counted.sort(key=lambda x: x["count_articles"], reverse=True)

    # -----------------------------
    # FINAL SUMMARY STRUCTURE
    # -----------------------------
    summary = {
        "count_unique": len(unique_affs),
        "counts_total": sum(aff_counts_total.values()),
        "count_article": total_articles,
        "count_articles_with_affs": articles_with_affs_count,
        "most_common_affs": most_common_affs,
        "affs": unique_affs,
        "affs_counted": affs_counted
    }

    # -----------------------------
    # SAVE RESULTS
    # -----------------------------
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nAffiliation summary saved → {output_path}")
    print("=== Done ===\n")


if __name__ == "__main__":
    list_affs()
