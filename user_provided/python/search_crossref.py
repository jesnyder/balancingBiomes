import requests
import json
import csv
import os
import time

QUERY = "Halophyte AND Halophile"
BASE_URL = "https://api.crossref.org/works"
OUTPUT_DIR = "results/search_results"
CROSSREF_JSON = os.path.join(OUTPUT_DIR, "list_crossref.json")
CROSSREF_CSV = os.path.join(OUTPUT_DIR, "list_crossref.csv")
BATCH_DIR = os.path.join(OUTPUT_DIR, "crossref")
PER_PAGE = 100  # max results per request
RATE_LIMIT_SLEEP = 1  # seconds between requests

os.makedirs(BATCH_DIR, exist_ok=True)

def search_crossref():
    compiled_results = []
    offset = 0
    page_num = 1

    while True:
        params = {
            "query": QUERY,
            "rows": PER_PAGE,
            "offset": offset
        }
        print(f"Fetching CrossRef results offset {offset}...")
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code == 429:
            print("Rate limit hit, sleeping 60 seconds...")
            time.sleep(60)
            continue
        resp.raise_for_status()
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        if not items:
            break

        # Save each page
        batch_file = os.path.join(BATCH_DIR, f"{page_num:03d}_crossref.json")
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(items)} results to {batch_file}")

        # Compile results
        for item in items:
            compiled_results.append({
                "title": " ".join(item.get("title", [])),
                "authors": ", ".join([f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get("author", [])]),
                "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                "doi": item.get("DOI"),
                "url": item.get("URL"),
                "publisher": item.get("publisher"),
                "type": item.get("type"),
                "reference_count": item.get("reference-count", 0),
                "is_referenced_by_count": item.get("is-referenced-by-count", 0)
            })

        offset += PER_PAGE
        page_num += 1
        time.sleep(RATE_LIMIT_SLEEP)

    # Save compiled JSON
    with open(CROSSREF_JSON, "w", encoding="utf-8") as f:
        json.dump(compiled_results, f, indent=2, ensure_ascii=False)

    # Save compiled CSV
    fieldnames = ["title", "authors", "year", "doi", "url", "publisher", "type",
                  "reference_count", "is_referenced_by_count"]
    with open(CROSSREF_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(compiled_results)

    print(f"Compiled {len(compiled_results)} CrossRef results saved as JSON + CSV")
    return len(compiled_results)

if __name__ == "__main__":
    search_crossref()
