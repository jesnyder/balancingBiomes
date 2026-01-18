import os
import requests
import json
import csv
import time

RESULTS_DIR = "results/search_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

JSON_FILE = os.path.join(RESULTS_DIR, "list_openalex.json")
CSV_FILE = os.path.join(RESULTS_DIR, "list_openalex.csv")

QUERY = "Halophyte Halophile"
BASE_URL = "https://api.openalex.org/works"
PER_PAGE = 200  # max allowed per request
RATE_LIMIT_SLEEP = 1  # polite pause between requests


def search_openalex():
    print("Querying OpenAlex...")

    all_results = []
    cursor = "*"  # start cursor

    while cursor:
        params = {
            "search": QUERY,
            "per-page": PER_PAGE,
            "cursor": cursor
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            break

        for entry in results:
            # DOI handling
            doi = entry.get("doi")
            if doi and doi.startswith("https://doi.org/"):
                entry["doiURL"] = doi
                entry["doi"] = doi.replace("https://doi.org/", "")

            # Add "cited_by" if "cited_by_count" exists
            if "cited_by_count" in entry:
                entry["cited_by"] = entry["cited_by_count"]

            all_results.append(entry)

        # Update cursor for next page
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        # Polite pause to avoid hitting rate limits
        time.sleep(RATE_LIMIT_SLEEP)

    print(f"Total OpenAlex results fetched: {len(all_results)}")

    # Save JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Save CSV
    if all_results:
        fieldnames = sorted({k for entry in all_results for k in entry.keys()})
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)

    print(f"Saved OpenAlex results: {JSON_FILE}, {CSV_FILE}")


if __name__ == "__main__":
    search_openalex()
