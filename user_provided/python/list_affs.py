#!/usr/bin/env python3
"""
Date: 2026-02-20

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
    Main function to extract affiliations, count their occurrences,
    and summarize results in a structured dictionary.
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
    all_affs = []  # all affiliations including duplicates
    articles_with_affs_count = 0
    affs_article_counter = defaultdict(int)  # counts number of articles each affiliation appears in

    # -----------------------------
    # PROCESS EACH ARTICLE
    # -----------------------------
    for idx, article in enumerate(articles, start=1):
        article_has_aff = False
        authors = article.get("authors", [])

        # Track unique affiliations per article to avoid double-counting in articles
        unique_article_affs = set()

        for author in authors:
            # Some authors are strings instead of dicts, skip safely
            if not isinstance(author, dict):
                continue

            affs = author.get("affiliation", [])
            # Ensure affiliations is a list
            if isinstance(affs, str):
                affs = [affs]
            elif not isinstance(affs, list):
                affs = []

            for aff in affs:
                aff = aff.strip()
                if aff:
                    all_affs.append(aff)
                    unique_article_affs.add(aff)
                    article_has_aff = True

        # Count each unique affiliation for this article
        for aff in unique_article_affs:
            affs_article_counter[aff] += 1

        if article_has_aff:
            articles_with_affs_count += 1

        if idx % 100 == 0 or idx == total_articles:
            print(f"Processed {idx}/{total_articles} articles...")

    # -----------------------------
    # SUMMARIZE AFFILIATIONS
    # -----------------------------
    aff_counts_total = Counter(all_affs)
    unique_affs = sorted(aff_counts_total.keys())

    # Top 10 most common affiliations
    most_common_affs = [name for name, _ in aff_counts_total.most_common(10)]

    # Prepare affs_counted list sorted by count_articles descending
    affs_counted = []
    for aff in unique_affs:
        affs_counted.append({
            "name": aff,
            "count": aff_counts_total[aff],
            "count_articles": affs_article_counter.get(aff, 0)
        })
    affs_counted.sort(key=lambda x: x["count_articles"], reverse=True)

    # -----------------------------
    # FINAL SUMMARY DICTIONARY
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
    # SAVE SUMMARY
    # -----------------------------
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAffiliation summary saved → {output_path}")
    print("=== Done ===\n")


if __name__ == "__main__":
    list_affs()
