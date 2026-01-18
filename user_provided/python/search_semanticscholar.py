import os
import requests
import json
import csv
import time

# === Configuration ===
QUERY = '"Halophyte" AND "Halophile"'
SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper/"
OUTPUT_DIR = os.path.join("results", "search_results")
SS_DIR = os.path.join(OUTPUT_DIR, "semantic_scholar")
JSON_COMPILED = os.path.join(OUTPUT_DIR, "list_semanticscholar.json")
CSV_COMPILED = os.path.join(OUTPUT_DIR, "list_semanticscholar.csv")

SEARCH_FIELDS = "title,authors,year,doi,url,citationCount"
FULL_FIELDS = "title,abstract,authors,year,venue,doi,url,fieldsOfStudy,referenceCount,citationCount,influentialCitationCount"

LIMIT = 20
REQUEST_SLEEP = 10  # seconds between requests

os.makedirs(SS_DIR, exist_ok=True)

def fetch_full_metadata(paper_id):
    """Fetch complete metadata for a paper by paperId."""
    try:
        resp = requests.get(f"{PAPER_URL}{paper_id}", params={"fields": FULL_FIELDS})
        resp.raise_for_status()
        data = resp.json()
        data["cited_by"] = data.get("citationCount", 0)
        return data
    except requests.RequestException as e:
        print(f"Failed to fetch full metadata for paperId {paper_id}: {e}")
        return None

def collect_existing_batches():
    """Load JSON files in semantic_scholar folder to remove duplicates."""
    existing_papers = {}
    for fname in os.listdir(SS_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(SS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    papers = json.load(f)
                    for p in papers:
                        if "paperId" in p:
                            existing_papers[p["paperId"]] = p
                except json.JSONDecodeError:
                    print(f"Warning: Could not read {fname}, skipping")
    return existing_papers

def search_semanticscholar():
    compiled_results = collect_existing_batches()
    offset = 0
    page_num = 1

    while True:
        params = {
            "query": QUERY,
            "limit": LIMIT,
            "offset": offset,
            "fields": SEARCH_FIELDS
        }

        try:
            print(f"Fetching papers {offset + 1} to {offset + LIMIT}...")
            resp = requests.get(SEARCH_URL, params=params)
            if resp.status_code == 429:
                print(f"Rate limit hit. Sleeping 60s...")
                time.sleep(60)
                continue
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Search request error: {e}. Moving on to compilation.")
            break

        data = resp.json()
        papers = data.get("data", [])
        if not papers:
            print("No more papers found. Search complete.")
            break

        # Save raw batch JSON
        batch_filename = f"{page_num:03d}{LIMIT}_semanticscholar.json"
        batch_path = os.path.join(SS_DIR, batch_filename)
        with open(batch_path, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(papers)} papers to {batch_filename}")

        # Fetch full metadata
        for paper in papers:
            paper_id = paper.get("paperId")
            if not paper_id or paper_id in compiled_results:
                continue
            full_data = fetch_full_metadata(paper_id)
            if full_data:
                compiled_results[paper_id] = full_data
            time.sleep(REQUEST_SLEEP)

        offset += LIMIT
        page_num += 1

    # Convert compiled_results dict to list
    all_papers = list(compiled_results.values())

    # Save compiled JSON
    with open(JSON_COMPILED, "w", encoding="utf-8") as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)

    # Save CSV overview
    fieldnames = ["title", "year", "doi", "url", "citationCount", "cited_by"]
    with open(CSV_COMPILED, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for paper in all_papers:
            writer.writerow({
                "title": paper.get("title"),
                "year": paper.get("year"),
                "doi": paper.get("doi"),
                "url": paper.get("url"),
                "citationCount": paper.get("citationCount"),
                "cited_by": paper.get("cited_by")
            })

    print(f"\nCompiled {len(all_papers)} unique papers saved as JSON + CSV.")
    return all_papers

if __name__ == "__main__":
    search_semanticscholar()
