#!/usr/bin/env python3
"""
Date: 2026-02-22

Objective:
    Query the Global Biodiversity Information Facility (GBIF) Backbone Taxonomy
    using a list of organism scientific names and build structured metadata.

Dependencies:
    - requests  (HTTP requests to GBIF API)
    - json      (saving results)
    - os        (file and directory handling)
    - time      (rate limiting to be polite to API)

Design Notes:
    • Written for clarity and novice understanding
    • Prints progress updates for troubleshooting
    • Saves progress after EACH organism to prevent data loss
"""

import requests
import json
import os
import time


def query_gbif():
    """Main function to query GBIF and build metadata."""

    input_file = "user_provided/admin/organisms.csv"
    output_file = "results/query/gbif/query_gbif.json"

    print("=== Starting GBIF query process ===")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # -----------------------------
    # LOAD ORGANISM LIST
    # -----------------------------
    print("Loading organism list...")
    with open(input_file, "r", encoding="utf-8") as f:
        organisms = sorted(set(line.strip() for line in f if line.strip()))

    print(f"Loaded {len(organisms)} unique organisms.\n")

    results = []
    missing = []
    key_counts = {}

    # -----------------------------
    # QUERY GBIF FOR EACH ORGANISM
    # -----------------------------
    for idx, name in enumerate(organisms, start=1):
        print(f"[{idx}/{len(organisms)}] Querying: {name}")

        try:
            # -----------------------------
            # STEP 1 — MATCH NAME
            # -----------------------------
            match_url = "https://api.gbif.org/v1/species/match"
            match_response = requests.get(match_url, params={"name": name}, timeout=30)
            match_data = match_response.json()

            taxon_key = match_data.get("usageKey")
            if not taxon_key:
                print("  ❌ No GBIF match found.")
                missing.append(name)
                save_data(results, missing, key_counts, output_file)
                continue

            # -----------------------------
            # STEP 2 — SPECIES METADATA
            # -----------------------------
            species_url = f"https://api.gbif.org/v1/species/{taxon_key}"
            species_data = requests.get(species_url, timeout=30).json()

            # Extract accepted name safely
            accepted_name = None
            if isinstance(species_data.get("accepted"), dict):
                accepted_name = species_data["accepted"].get("scientificName")

            # -----------------------------
            # STEP 3 — SYNONYMS
            # -----------------------------
            syn_url = f"https://api.gbif.org/v1/species/{taxon_key}/synonyms"
            syn_data = requests.get(syn_url, timeout=30).json()
            synonyms = [
                s.get("scientificName")
                for s in syn_data.get("results", [])
                if s.get("scientificName")
            ]

            # -----------------------------
            # STEP 4 — VERNACULAR NAMES
            # -----------------------------
            vern_url = f"https://api.gbif.org/v1/species/{taxon_key}/vernacularNames"
            vern_data = requests.get(vern_url, timeout=30).json()
            vernacular_names = [
                v.get("vernacularName")
                for v in vern_data.get("results", [])
                if v.get("vernacularName")
            ]

            # -----------------------------
            # STEP 5 — OCCURRENCE COUNTS BY COUNTRY
            # -----------------------------
            occ_url = "https://api.gbif.org/v1/occurrence/search"
            occ_params = {"taxonKey": taxon_key, "limit": 0, "facet": "country"}
            occ_data = requests.get(occ_url, params=occ_params, timeout=30).json()

            country_counts = {}
            for facet in occ_data.get("facets", []):
                if facet.get("field") == "COUNTRY":
                    for entry in facet.get("counts", []):
                        country_counts[entry["name"]] = entry["count"]

            # -----------------------------
            # BUILD ORGANISM DICTIONARY
            # -----------------------------
            organism_dict = {
                "queryName": name,
                "gbif_url": f"https://www.gbif.org/species/{taxon_key}",
                "scientificName": species_data.get("scientificName"),
                "taxonKey": taxon_key,
                "taxonRank": species_data.get("rank"),
                "taxonomicStatus": species_data.get("taxonomicStatus"),
                "acceptedNameUsage": accepted_name,
                "kingdom": species_data.get("kingdom"),
                "phylum": species_data.get("phylum"),
                "class": species_data.get("class"),
                "order": species_data.get("order"),
                "family": species_data.get("family"),
                "genus": species_data.get("genus"),
                "species": species_data.get("species"),
                "synonyms": synonyms,
                "vernacularNames": vernacular_names,
                "occurrenceCountsByCountry": country_counts,
                "habitat": species_data.get("habitat"),
            }

            # Track key presence statistics
            for key, value in organism_dict.items():
                if value not in (None, [], {}):
                    key_counts[key] = key_counts.get(key, 0) + 1

            results.append(organism_dict)

            print("  ✅ Success")

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            missing.append(name)

        # Save progress after each organism
        save_data(results, missing, key_counts, output_file)

        # Polite rate limiting
        time.sleep(1)

    print("\n=== GBIF query complete ===")
    print(f"Total organisms processed: {len(organisms)}")
    print(f"Missing organisms: {len(missing)}")


def save_data(results, missing, key_counts, output_file):
    """Save progress to JSON file after each organism."""

    total = len(results)

    # Build keys summary with correct percent calculation
    keys_summary = []
    for key in sorted(key_counts.keys()):
        count = key_counts[key]
        percent = round((count / total) * 100, 2) if total else 0
        keys_summary.append({
            "name": key,
            "count": count,
            "percent": percent
        })

    output_data = {
        "organisms_count": total,
        "organisms_missing": sorted(missing),
        "keys": keys_summary,
        "organisms": results
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("  💾 Progress saved.")


if __name__ == "__main__":
    query_gbif()
