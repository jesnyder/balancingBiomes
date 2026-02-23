#!/usr/bin/env python3
"""
Date: 2026-02-22

Objective:
    Count organism mentions in compiled articles using GBIF metadata.
    Matching includes:
        • Scientific name
        • Synonyms
        • Vernacular names
        • Abbreviated genus (e.g., A. occidentalis)

    Matching improvements:
        • Unicode normalization
        • Punctuation normalization
        • Whitespace normalization

Dependencies:
    Python 3.8+
"""

import json
import os
import re
import unicodedata
from collections import Counter

def count_organisms():
    """
    Main function to count organism mentions in compiled articles.
    """

    # -----------------------------
    # FILE PATHS
    # -----------------------------
    gbif_path = "results/query/gbif/query_gbif.json"
    articles_path = "results/query/compiled_articles.json"
    output_path = "results/counts/count_organisms.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # -----------------------------
    # TEXT NORMALIZATION UTILITIES
    # -----------------------------
    def normalize_text(text):
        """
        Normalize text for robust matching.

        Steps:
        1. Unicode normalize (removes hidden characters)
        2. Convert to lowercase
        3. Replace punctuation with spaces
        4. Collapse whitespace
        """
        if not text:
            return ""

        # Normalize unicode (NFKD removes hidden formatting)
        text = unicodedata.normalize("NFKD", str(text))

        # Convert to lowercase
        text = text.lower()

        # Replace punctuation with space
        text = re.sub(r"[^\w\s]", " ", text)

        # Collapse multiple whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    print("\n=== Loading GBIF organism metadata ===")
    with open(gbif_path, "r", encoding="utf-8") as f:
        gbif_data = json.load(f)

    organisms = gbif_data.get("organisms", [])
    print(f"Loaded {len(organisms)} organisms.")

    print("\n=== Loading compiled articles ===")
    with open(articles_path, "r", encoding="utf-8") as f:
        articles_data = json.load(f)

    articles = articles_data.get("articles", [])
    print(f"Loaded {len(articles)} articles.")

    # -----------------------------
    # PREPARE ARTICLE TEXT
    # -----------------------------
    print("\n=== Normalizing article text ===")
    article_texts = []
    article_citations = []

    for idx, article in enumerate(articles, start=1):
        parts = []

        # Gather ALL values from article dictionary
        for value in article.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend([str(v) for v in value])
            elif isinstance(value, dict):
                parts.extend([str(v) for v in value.values()])

        full_text = normalize_text(" ".join(parts))
        article_texts.append(full_text)

        # Citation logic
        citations = article.get("is_referenced_by_count") or article.get("num_citations") or 0
        if isinstance(citations, list):
            citations = citations[0] if citations else 0
        article_citations.append(int(citations))

        if idx % 500 == 0 or idx == len(articles):
            print(f"Processed {idx}/{len(articles)} articles")

    # -----------------------------
    # COUNT ORGANISMS
    # -----------------------------
    print("\n=== Counting organism mentions ===")

    organisms_found = 0
    organism_results = []

    for idx, org in enumerate(organisms, start=1):
        # Gather name variants
        variants = set()

        query_name = org.get("queryName")
        scientific_name = org.get("scientificName")
        species = org.get("species")
        #synonyms = org.get("synonyms", [])
        vernacular = org.get("vernacularNames", [])

        # Add primary names
        for name in [query_name, scientific_name, species]:
            if name:
                variants.add(normalize_text(name))

        """
        # Add synonyms
        for name in synonyms:
            variants.add(normalize_text(name))
        """

        # Add vernacular names
        for name in vernacular:
            variants.add(normalize_text(name))

        # -----------------------------
        # ADD ABBREVIATED GENUS MATCH
        # -----------------------------
        if species:
            parts = species.split()
            if len(parts) >= 2:
                abbreviated = f"{parts[0][0]}. {' '.join(parts[1:])}"
                normalized_abbrev = normalize_text(abbreviated)
                variants.add(normalized_abbrev)

                # Save abbreviated synonym for transparency
                org.setdefault("synonyms", []).append(abbreviated)

        # Remove empty strings
        variants.discard("")

        # Count matches
        count = 0
        count_2 = 0

        for text, cites in zip(article_texts, article_citations):
            if any(variant in text for variant in variants):
                count += 1
                if cites >= 2:
                    count_2 += 1

        if count > 0:
            organisms_found += 1

        # Save results
        org["count"] = count
        org["count_2"] = count_2
        organism_results.append(org)

        print(f"{idx}/{len(organisms)} → {query_name}: {count}")

    # -----------------------------
    # SUMMARY STATISTICS
    # -----------------------------
    organisms_not_found = len(organisms) - organisms_found

    # Top 5 organisms
    organism_most = sorted(
        organism_results,
        key=lambda x: x["count"],
        reverse=True
    )[:5]

    organism_most_names = [o["queryName"] for o in organism_most]

    # Key statistics
    key_counter = Counter()
    for org in organism_results:
        for key, value in org.items():
            if value:
                key_counter[key] += 1

    keys_summary = []
    total_orgs = len(organism_results)
    for key in sorted(key_counter):
        count = key_counter[key]
        percent = round((count / total_orgs) * 100, 2)
        keys_summary.append({"name": key, "count": count, "percent": percent})

    # -----------------------------
    # FINAL OUTPUT
    # -----------------------------
    output = {
        "organisms_count": len(organisms),
        "organisms_found": organisms_found,
        "organisms_not_found": organisms_not_found,
        "organism_most": organism_most_names,
        "keys": keys_summary,
        "organisms": organism_results
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved results → {output_path}")
    print("=== Done ===\n")


if __name__ == "__main__":
    count_organisms()
