#!/usr/bin/env python3
"""
detail_species.py

Retrieve species details including kingdom classification and halotolerance.

Databases used:
- GBIF API (primary)
- NCBI Taxonomy API (secondary)
- Local halotolerance list (user_provided/halotolerant_species.csv)

Outputs:
- results/species_detailed.json
- results/species_detailed.csv

Terminal prints full diagnostic info for troubleshooting.
"""

import os
import csv
import json
import requests
import time
import certifi

# ------------------ Configuration ------------------
SPECIES_LIST = "user_provided/species_list.csv"
HALOTOLERANT_LIST = "user_provided/halotolerant_species.csv"
OUTPUT_DIR = "results"
JSON_FILE = os.path.join(OUTPUT_DIR, "species_detailed.json")
CSV_FILE = os.path.join(OUTPUT_DIR, "species_detailed.csv")

GBIF_API = "https://api.gbif.org/v1/species/match"
NCBI_API = "https://api.ncbi.nlm.nih.gov/taxonomy/v0/name/"

REQUEST_SLEEP = 1  # seconds between requests to avoid rate limits
TIMEOUT = 30       # seconds

# ------------------ Helper Functions ------------------

def load_species_list():
    with open(SPECIES_LIST, newline="", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_halotolerant_list():
    halotolerant = set()
    if os.path.exists(HALOTOLERANT_LIST):
        with open(HALOTOLERANT_LIST, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                halotolerant.add(row[0].strip())
    return halotolerant

def query_gbif(species_name):
    url = GBIF_API
    params = {"name": species_name}
    print(f"[GBIF] Querying {species_name}: {url}?name={species_name}")
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT, verify=certifi.where())
        resp.raise_for_status()
        data = resp.json()
        kingdom = data.get("kingdom")
        usageKey = data.get("usageKey")
        return {"kingdom": kingdom, "usageKey": usageKey}
    except requests.RequestException as e:
        print(f"[GBIF] Error for {species_name}: {e}")
        return None

def query_ncbi(species_name):
    url = f"{NCBI_API}{species_name}"
    print(f"[NCBI] Querying {species_name}: {url}")
    try:
        resp = requests.get(url, timeout=TIMEOUT, verify=certifi.where())
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            kingdom = data[0].get("kingdom")
            return {"kingdom": kingdom}
        else:
            return None
    except requests.RequestException as e:
        print(f"[NCBI] Error for {species_name}: {e}")
        return None

# ------------------ Main Function ------------------

def detail_species():
    print("detail_species running")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    species_list = load_species_list()
    halotolerant_set = load_halotolerant_list()

    detailed_results = []

    for idx, species_name in enumerate(species_list, start=1):
        print(f"[{idx}/{len(species_list)}] Processing: {species_name}")

        record = {"species": species_name, "url": None, "kingdom": None, "halotolerant": "No"}

        # Check halotolerance from local list
        if species_name in halotolerant_set:
            record["halotolerant"] = "Yes"

        # Query GBIF first
        gbif_result = query_gbif(species_name)
        time.sleep(REQUEST_SLEEP)

        if gbif_result and gbif_result.get("usageKey"):
            record["kingdom"] = gbif_result.get("kingdom")
            record["url"] = f"https://www.gbif.org/species/{gbif_result['usageKey']}"
        else:
            # Query NCBI as fallback
            ncbi_result = query_ncbi(species_name)
            time.sleep(REQUEST_SLEEP)
            if ncbi_result:
                record["kingdom"] = ncbi_result.get("kingdom")

        if not record["kingdom"]:
            print(f"[WARN] No kingdom info found for {species_name}")

        if not record["url"] and gbif_result and gbif_result.get("usageKey"):
            record["url"] = f"https://www.gbif.org/species/{gbif_result['usageKey']}"

        detailed_results.append(record)

    # Save JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)

    # Save CSV
    fieldnames = ["species", "kingdom", "url", "halotolerant"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_results)

    print(f"\nCompleted: {len(detailed_results)} species processed")
    print(f"Results saved as JSON: {JSON_FILE} and CSV: {CSV_FILE}")

# ------------------ Run Script ------------------
if __name__ == "__main__":
    detail_species()
