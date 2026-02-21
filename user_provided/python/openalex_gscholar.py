#!/usr/bin/env python3
"""
Date: 2026-02-19

Objective:
    Full enrichment pipeline for CrossRef Google Scholar articles:
        - Add OpenAlex metadata (including abstract)
        - Add Semantic Scholar metadata (including abstract)
        - Attempt missing DOI recovery via OpenAlex and CrossRef using title matching
        - Save progress after each article

Requirements:
    - Keep articles without DOI
    - Use DOI as primary key
    - Store OpenAlex under 'openalex' key
    - Store Semantic Scholar under 'semanticscholar' key
    - Wait >=5 seconds between API requests
    - Validate title matches with string similarity threshold 0.85
    - Maintain output schema with counts, keys, missing_crossref

Dependencies:
    - Python 3.8+
    - requests
    - json
    - time
    - os
    - difflib
"""

import json
import os
import time
import requests
from difflib import SequenceMatcher
from urllib.parse import quote


def openalex_gscholar():
    """Main function to enrich CrossRef Google Scholar dataset with OpenAlex and Semantic Scholar."""

    input_path = "results/query/gscholar/crossref_gscholar.json"
    output_path = "results/query/gscholar/openalex_gscholar.json"

    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    missing_crossref = data.get("missing_crossref", [])

    print(f"[INFO] Loaded {len(articles)} articles from CrossRef-enriched dataset.")

    # -------------------------
    # Helper functions
    # -------------------------
    def similar(a, b):
        """Compute string similarity ratio for title matching."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def parse_openalex_abstract(oa_data):
        """
        Convert OpenAlex abstract_inverted_index to plain text string.
        Returns None if abstract is missing.
        """
        if not oa_data:
            return None
        inverted_index = oa_data.get("abstract_inverted_index")
        if not inverted_index:
            return None  # Abstract not available

        words = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word

        return " ".join([words[i] for i in sorted(words)])

    def save_progress():
        """Save dataset and update counts after each article."""
        def citation_count(a):
            return a.get("is-referenced-by-count", 0)

        sorted_articles = sorted(articles, key=citation_count, reverse=True)
        articles_count_2 = sum(1 for a in sorted_articles if a.get("is-referenced-by-count", 0) >= 2)
        keys_set = set()
        for a in sorted_articles:
            keys_set.update(a.keys())

        output_data = {
            "articles_count": len(sorted_articles),
            "articles_count_2": articles_count_2,
            "articles_with_doi": sum(1 for a in sorted_articles if a.get("doi")),
            "articles_without_doi": sum(1 for a in sorted_articles if not a.get("doi")),
            "keys": sorted(keys_set),
            "missing_crossref": sorted(missing_crossref),
            "articles": sorted_articles
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print("[SAVE] Progress saved.")

    # -------------------------
    # API query functions
    # -------------------------
    def fetch_openalex(doi):
        url = f"https://api.openalex.org/works/https://doi.org/{doi}"
        print("[WAIT] 5 sec before OpenAlex request...")
        time.sleep(5)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            print(f"[ERROR] OpenAlex request failed: {e}")
        return None

    def fetch_semantic_scholar(doi):
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,authors,citationCount"
        print("[WAIT] 5 sec before Semantic Scholar request...")
        time.sleep(5)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            print(f"[ERROR] Semantic Scholar request failed: {e}")
        return None

    def recover_doi_openalex(title):
        query = quote(f'title:"{title}"')
        url = f"https://api.openalex.org/works?filter=title.search:{query}&per-page=5"
        print("[WAIT] 5 sec before OpenAlex DOI recovery request...")
        time.sleep(5)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("results", [])
        except requests.RequestException as e:
            print(f"[ERROR] OpenAlex DOI recovery failed: {e}")
        return []

    def recover_doi_crossref(title):
        query = quote(title)
        url = f"https://api.crossref.org/works?query.title={query}&rows=5"
        print("[WAIT] 5 sec before CrossRef DOI recovery request...")
        time.sleep(5)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("items", [])
        except requests.RequestException as e:
            print(f"[ERROR] CrossRef DOI recovery failed: {e}")
        return []

    # -------------------------
    # Process articles
    # -------------------------
    for idx, article in enumerate(articles, start=1):
        raw_title = article.get("title", "")
        if isinstance(raw_title, list) and len(raw_title) > 0:
            title = str(raw_title[0]).strip()
        else:
            title = str(raw_title).strip()

        doi = article.get("doi")

        print(f"\n[PROCESS] Article {idx}/{len(articles)}: '{title}'")

        # -------------------------
        # Missing DOI recovery
        # -------------------------
        if not doi:
            print("[INFO] Attempting missing DOI recovery...")
            doi_found = None

            oa_results = recover_doi_openalex(title)
            for r in oa_results:
                oa_title = r.get("title", "")
                if similar(title, oa_title) >= 0.85:
                    doi_found = r.get("doi")
                    if doi_found:
                        article["doi"] = doi_found
                        article["openalex"] = r
                        article["openalex"]["abstract_text"] = parse_openalex_abstract(r)
                        print(f"[FOUND] DOI via OpenAlex recovery: {doi_found}")
                        break

            if not doi_found:
                cr_results = recover_doi_crossref(title)
                for r in cr_results:
                    cr_title = r.get("title", [""])[0]
                    if similar(title, cr_title) >= 0.85:
                        doi_found = r.get("DOI")
                        if doi_found:
                            article["doi"] = doi_found
                            print(f"[FOUND] DOI via CrossRef recovery: {doi_found}")
                            break

            if not doi_found:
                print("[MISS] Could not recover DOI.")

        # -------------------------
        # Enrichment with DOI
        # -------------------------
        doi = article.get("doi")
        if doi:
            # OpenAlex enrichment
            if "openalex" not in article:
                oa_metadata = fetch_openalex(doi)
                if oa_metadata:
                    article["openalex"] = oa_metadata
                    article["openalex"]["abstract_text"] = parse_openalex_abstract(oa_metadata)
                    print("[SUCCESS] OpenAlex metadata added.")

            # Semantic Scholar enrichment
            if "semanticscholar" not in article:
                ss_metadata = fetch_semantic_scholar(doi)
                if ss_metadata:
                    article["semanticscholar"] = ss_metadata
                    print("[SUCCESS] Semantic Scholar metadata added.")
        else:
            print("[INFO] No DOI → enrichment skipped.")

        # Save after each article
        save_progress()

    # -------------------------
    # Final save
    # -------------------------
    print("\n[COMPLETE] Full OpenAlex + Semantic Scholar enrichment finished.")
    save_progress()


if __name__ == "__main__":
    openalex_gscholar()
