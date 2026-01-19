import requests
import json
import time
from pathlib import Path

# -------------------------------
# Configuration
# -------------------------------

QUERY = "Halophyte AND Halophile"          # Search query
BASE_URL = "https://api.crossref.org/works"  # CrossRef API endpoint

# Output paths
OUTPUT_DIR = Path("results/search_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CROSSREF_JSON = OUTPUT_DIR / "list_crossref.json"  # Final enriched JSON

# Cache directory for intermediate DOI results
CACHE_DIR = OUTPUT_DIR / "crossref"
CACHE_DIR.mkdir(exist_ok=True)

# Pagination and rate limits
PER_PAGE = 100        # Maximum results per request
SEARCH_SLEEP = 1      # Seconds between search requests
DOI_SLEEP = 3         # Seconds between DOI enrichment requests

# -------------------------------
# Main function
# -------------------------------
def search_crossref():
    """
    Main function to:
    1. Search CrossRef for "Halophyte AND Halophile"
    2. Save intermediate results and cache DOIs locally
    3. Add 'cited_by' and DOI-based 'url' fields
    4. Enrich each DOI with metadata (abstract, publication year, message, snippet)
    5. Print abstracts for verification
    6. Save final enriched results to JSON
    """

    compiled_results = []

    # -------------------------------
    # Step 1: Initial CrossRef search
    # -------------------------------
    offset = 0
    page_num = 1
    print(f"[INFO] Starting CrossRef search for query: {QUERY}")

    while True:
        params = {"query": QUERY, "rows": PER_PAGE, "offset": offset}
        print(f"[INFO] Fetching results offset {offset} (page {page_num})...")
        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            if resp.status_code == 429:
                print("[WARNING] Rate limit hit. Sleeping 60 seconds...")
                time.sleep(60)
                continue
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to fetch CrossRef results: {e}")
            break

        items = resp.json().get("message", {}).get("items", [])
        if not items:
            print("[INFO] No more items returned. Ending search.")
            break

        # Process each result
        for item in items:
            doi = item.get("DOI")
            entry = {
                "title": " ".join(item.get("title", [])),
                "authors": ", ".join([f"{a.get('given','')} {a.get('family','')}".strip()
                                      for a in item.get("author", [])]),
                "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                "doi": doi,
                "url": f"https://doi.org/{doi}" if doi else None,
                "publisher": item.get("publisher"),
                "type": item.get("type"),
                "reference_count": item.get("reference-count", 0),
                "is_referenced_by_count": item.get("is-referenced-by-count", 0)
            }

            # Add 'cited_by' from 'is_referenced_by_count'
            entry["cited_by"] = entry["is_referenced_by_count"]

            compiled_results.append(entry)

        # Save intermediate progress
        with open(CROSSREF_JSON, "w", encoding="utf-8") as f:
            json.dump(compiled_results, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved {len(items)} results from page {page_num} (total {len(compiled_results)})")

        offset += PER_PAGE
        page_num += 1
        time.sleep(SEARCH_SLEEP)

    print(f"[INFO] Initial CrossRef search completed. Total entries: {len(compiled_results)}")

    # -------------------------------
    # Step 2: Enrich each DOI with full metadata
    # -------------------------------
    total = len(compiled_results)
    print(f"[INFO] Starting DOI enrichment for {total} entries...")

    for i, entry in enumerate(compiled_results, start=1):
        doi = entry.get("doi")
        if not doi:
            continue

        # Cache file path
        cache_file = CACHE_DIR / f"{doi.replace('/', '_')}.json"
        if cache_file.exists():
            print(f"[INFO] Loading cached metadata for DOI {doi}")
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            # Query CrossRef for DOI metadata
            url = f"{BASE_URL}/{doi}"
            headers = {"User-Agent": "search_crossref_script/1.0 (mailto:you@example.com)"}
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get("message", {})
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    print(f"[WARNING] DOI {doi} returned status {resp.status_code}")
                    continue
            except Exception as e:
                print(f"[ERROR] Exception querying DOI {doi}: {e}")
                continue

            time.sleep(DOI_SLEEP)

        # Extract textual metadata
        abstract = data.get("abstract")
        snippet = data.get("short-container-title") or data.get("short-title") or None

        # Print abstract to terminal for verification
        if abstract:
            print(f"[DOI {i}/{total}] Abstract for DOI {doi}:\n{abstract}\n")
        else:
            print(f"[DOI {i}/{total}] No abstract found for DOI {doi}")

        # Add metadata to entry
        if abstract:
            entry["abstract"] = abstract
        if snippet:
            entry["snippet"] = snippet

        # Add full CrossRef message for completeness
        entry["crossref_message"] = data

        # Update publication year if present
        pub_date = data.get("published-print", data.get("published-online"))
        if pub_date and "date-parts" in pub_date:
            entry["year"] = pub_date["date-parts"][0][0]

        # Save progress incrementally
        with open(CROSSREF_JSON, "w", encoding="utf-8") as f:
            json.dump(compiled_results, f, indent=2, ensure_ascii=False)

        print(f"[PROGRESS] DOI enrichment {i}/{total} complete. Progress saved.")

    print(f"[INFO] DOI enrichment complete for all {total} entries.")
    print(f"[INFO] Final enriched results saved to {CROSSREF_JSON}")

    return compiled_results


# -------------------------------
# Execute if run directly
# -------------------------------
if __name__ == "__main__":
    search_crossref()
