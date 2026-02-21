#!/usr/bin/env python3
"""
Date: 2026-02-20

Objective:
    Enrich CrossRef articles with metadata from OpenAlex and Semantic Scholar.
    Save progress after each article. Deduplicate by DOI and summarize enriched data.

Dependencies:
    Python 3.8+
    requests → pip install requests
"""

import os
import json
import time
import requests

def openalex_crossref():
    """
    Main function to enrich CrossRef articles using OpenAlex and Semantic Scholar.
    Articles are enriched one at a time, progress is saved after each article.
    """

    # -----------------------------
    # CONFIGURATION
    # -----------------------------
    input_file = "results/query/crossref/compile_crossref.json"
    output_file = "results/query/crossref/openalex_crossref.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    openalex_base = "https://api.openalex.org/works/"
    semanticscholar_base = "https://api.semanticscholar.org/graph/v1/paper/"

    print("\n=== OpenAlex & Semantic Scholar Enrichment Started ===")

    # -----------------------------
    # LOAD COMPILED CROSSREF ARTICLES
    # -----------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    print(f"Loaded {len(articles)} articles from {input_file}")

    seen_dois = set()
    duplicates = 0

    # -----------------------------
    # FUNCTION TO QUERY OPENALEX
    # -----------------------------
    def query_openalex(doi=None, title=None):
        """Query OpenAlex by DOI or fallback title. Return metadata dict or None."""
        if doi:
            url = f"{openalex_base}https://doi.org/{doi}"
        elif title:
            url = f"{openalex_base}?filter=title.search:{requests.utils.quote(title)}"
        else:
            return None

        try:
            time.sleep(2)
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                if title and "results" in result:
                    for r in result["results"]:
                        if r.get("title", "").lower() == title.lower():
                            return r
                    return None
                return result
            else:
                print(f"⚠ OpenAlex request failed ({resp.status_code}) DOI={doi} Title={title}")
                return None
        except Exception as e:
            print(f"⚠ OpenAlex exception: {e} DOI={doi} Title={title}")
            return None

    # -----------------------------
    # FUNCTION TO QUERY SEMANTIC SCHOLAR
    # -----------------------------
    def query_semanticscholar(doi=None, title=None):
        """Query Semantic Scholar by DOI or title. Return metadata dict or None."""
        paper_id = f"DOI:{doi}" if doi else None
        if paper_id:
            url = f"{semanticscholar_base}{paper_id}?fields=title,abstract,authors,citationCount,year,venue"
            try:
                time.sleep(2)
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
                else:
                    print(f"⚠ Semantic Scholar request failed ({resp.status_code}) DOI={doi}")
                    return None
            except Exception as e:
                print(f"⚠ Semantic Scholar exception: {e} DOI={doi}")
                return None
        elif title:
            search_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={requests.utils.quote(title)}&limit=1&fields=title,abstract,authors,citationCount,year,venue"
            try:
                time.sleep(2)
                resp = requests.get(search_url, timeout=30)
                if resp.status_code == 200:
                    res = resp.json()
                    if res.get("data"):
                        return res["data"][0]
                return None
            except Exception as e:
                print(f"⚠ Semantic Scholar exception: {e} Title={title}")
                return None
        return None

    # -----------------------------
    # ENRICH ARTICLES ONE BY ONE
    # -----------------------------
    for idx, article in enumerate(articles, start=1):
        doi = article.get("doi")
        title = article.get("title")

        # Deduplicate by DOI
        if doi:
            norm_doi = doi.lower().strip()
            if norm_doi in seen_dois:
                duplicates += 1
                continue
            seen_dois.add(norm_doi)

        print(f"\n[{idx}/{len(articles)}] Processing DOI={doi} Title={title}")

        # --- OpenAlex enrichment ---
        oa_result = query_openalex(doi=doi, title=title)
        article["openalex"] = oa_result
        if oa_result:
            print("✓ OpenAlex data added")
        else:
            print("⚠ OpenAlex data not found")

        # --- Semantic Scholar enrichment ---
        ss_result = query_semanticscholar(doi=doi, title=title)
        article["semanticscholar"] = ss_result
        if ss_result:
            print("✓ Semantic Scholar data added")
        else:
            print("⚠ Semantic Scholar data not found")

        # -----------------------------
        # SAVE PROGRESS AFTER EACH ARTICLE
        # -----------------------------
        articles_found_oa = sum(1 for a in articles if a.get("openalex"))
        articles_found_ss = sum(1 for a in articles if a.get("semanticscholar"))
        articles_not_found = sum(1 for a in articles if not a.get("openalex") and not a.get("semanticscholar"))
        articles_not_list = [
            a.get("doi") or a.get("title")
            for a in articles
            if not a.get("openalex") and not a.get("semanticscholar")
        ]

        # Compute key summary
        key_counts = {}
        for a in articles:
            for key, val in a.items():
                if val not in (None, [], ""):
                    key_counts[key] = key_counts.get(key, 0) + 1
        keys_summary = [
            {"name": k, "count": c, "percent": round((c / len(articles)) * 100, 2)}
            for k, c in sorted(key_counts.items())
        ]

        summary = {
            "article_count": len(articles),
            "articles_found_oa": articles_found_oa,
            "articles_found_ss": articles_found_ss,
            "articles_not_found": articles_not_found,
            "articles_not_list": articles_not_list,
            "keys": keys_summary,
            "duplicates": duplicates,
            "articles": articles
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"Saved progress → {output_file}")

    print("\n✅ OpenAlex & Semantic Scholar enrichment complete!")

if __name__ == "__main__":
    openalex_crossref()
