#!/usr/bin/env python3
"""
Date: 2026-02-20

Objective:
    Compile CrossRef articles from DOI search and topic search,
    deduplicate by DOI while merging metadata, summarize, and save.

Dependencies:
    Python 3.8+
"""

import os
import json
from collections import defaultdict

def compile_crossref():
    """
    Main function to combine, deduplicate, and summarize CrossRef articles
    from DOI search and topic search.
    """

    # -----------------------------
    # CONFIGURATION
    # -----------------------------
    doi_file = "results/query/crossref/doi_crossref.json"
    topic_file = "results/query/crossref/query_crossref.json"
    compiled_file = "results/query/crossref/compile_crossref.json"

    os.makedirs(os.path.dirname(compiled_file), exist_ok=True)

    print("\n=== Compile CrossRef Articles ===")
    print("DOI search file:", os.path.abspath(doi_file))
    print("Topic search file:", os.path.abspath(topic_file))
    print("Compiled output file:", os.path.abspath(compiled_file))

    # -----------------------------
    # LOAD ARTICLES
    # -----------------------------
    all_articles_raw = []

    for file_path in [doi_file, topic_file]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles = data.get("articles", [])
                print(f"Loaded {len(articles)} articles from {file_path}")
                all_articles_raw.extend(articles)
        except Exception as e:
            print(f"⚠ Could not read {file_path}: {e}")

    print(f"Total articles before deduplication: {len(all_articles_raw)}")

    # -----------------------------
    # DEDUPLICATE AND MERGE BY DOI
    # -----------------------------
    merged_articles = {}
    duplicates = 0

    for article in all_articles_raw:
        doi = article.get("doi")
        if doi:
            doi = doi.lower().strip()
            article["doi"] = doi  # normalize DOI

            if doi in merged_articles:
                duplicates += 1
                # Merge metadata keys without losing information
                existing = merged_articles[doi]
                for key, value in article.items():
                    if value not in (None, [], ""):
                        if key not in existing or existing[key] in (None, [], ""):
                            existing[key] = value
                        elif isinstance(existing[key], list) and isinstance(value, list):
                            # Merge lists and remove duplicates
                            combined = existing[key] + [v for v in value if v not in existing[key]]
                            existing[key] = combined
                        elif isinstance(existing[key], dict) and isinstance(value, dict):
                            existing[key].update(value)
                merged_articles[doi] = existing
            else:
                merged_articles[doi] = article
        else:
            # Entry without DOI: include as-is, use id() to key uniquely
            merged_articles[id(article)] = article

    compiled_articles = list(merged_articles.values())
    print(f"Total articles after deduplication: {len(compiled_articles)}")
    print(f"Duplicate DOI entries merged: {duplicates}")

    # -----------------------------
    # SUMMARY METRICS
    # -----------------------------
    article_count = len(compiled_articles)
    articles_found = sum(1 for a in compiled_articles if a.get("doi"))
    articles_not_found = article_count - articles_found
    articles_not_list = [a.get("doi") for a in compiled_articles if not a.get("doi")]

    key_counts = {}
    for article in compiled_articles:
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

    # -----------------------------
    # SORT ARTICLES BY CITATION COUNT
    # -----------------------------
    compiled_articles.sort(
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
        "articles": compiled_articles
    }

    # -----------------------------
    # SAVE COMPILED JSON
    # -----------------------------
    with open(compiled_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n✅ Compilation complete!")
    print(f"Compiled summary saved → {os.path.abspath(compiled_file)}")
    print(f"Total articles compiled: {article_count}")


if __name__ == "__main__":
    compile_crossref()
