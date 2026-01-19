import json
import pandas as pd
from pathlib import Path
import requests
import time

# -------------------------------
# CrossRef API
# -------------------------------
CROSSREF_API = "https://api.crossref.org/works/"

def fetch_crossref_metadata(doi, cache):
    """
    Query CrossRef for a DOI with caching.
    Returns metadata dict with 'abstract' and 'year'.
    """
    doi_key = doi.strip().lower()
    if doi_key in cache:
        print(f"[CrossRef][Cache] Using cached metadata for DOI: {doi}")
        return cache[doi_key]

    headers = {"User-Agent": "compile_searches_script/1.0 (mailto:you@example.com)"}
    url = CROSSREF_API + doi
    try:
        print(f"[CrossRef] Querying DOI: {doi}")
        response = requests.get(url, headers=headers, timeout=10)
        metadata = {}
        if response.status_code == 200:
            message = response.json().get("message", {})
            # Abstract
            if "abstract" in message:
                metadata["abstract"] = message["abstract"]
            # Year
            pub_date = message.get("published-print", message.get("published-online"))
            if pub_date and "date-parts" in pub_date:
                metadata["year"] = pub_date["date-parts"][0][0]
            if metadata:
                print(f"[CrossRef] Metadata found for DOI: {doi}")
            else:
                print(f"[CrossRef] No abstract/year found for DOI: {doi}")
        else:
            print(f"[CrossRef] Warning: DOI {doi} returned status {response.status_code}")

        # Save to cache
        cache[doi_key] = metadata
        return metadata
    except Exception as e:
        print(f"[CrossRef] Error querying DOI {doi}: {e}")
        cache[doi_key] = {}  # Save empty to avoid retrying repeatedly
        return {}

# -------------------------------
# Enhance compiled entries with CrossRef
# -------------------------------
def enhance_compiled_with_crossref(compiled_entries, compiled_file, cache_file):
    """
    For each entry with a DOI, fetch abstract and year from CrossRef.
    Uses caching and incremental saving.
    """
    # Load or create cache
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            crossref_cache = json.load(f)
    else:
        crossref_cache = {}

    total = len(compiled_entries)
    print(f"[INFO] Enhancing {total} entries with CrossRef metadata...")

    for i, entry in enumerate(compiled_entries, start=1):
        doi = entry.get("doi")
        if doi:
            metadata = fetch_crossref_metadata(doi, crossref_cache)
            if metadata:
                for k, v in metadata.items():
                    if k not in entry or entry[k] in (None, "", []):
                        entry[k] = v

            # Save progress incrementally
            with open(compiled_file, "w", encoding="utf-8") as f:
                json.dump(compiled_entries, f, indent=2, ensure_ascii=False)
            # Save cache
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(crossref_cache, f, indent=2, ensure_ascii=False)

            print(f"[Progress] Entry {i}/{total} processed")
            time.sleep(3)  # rate limit

    print("[INFO] CrossRef enhancement complete.")

# -------------------------------
# Main compilation function
# -------------------------------
def compile_searches():
    """
    Main function:
    - Load JSON search results
    - Deduplicate & merge entries
    - Add cited_by and database info
    - Enhance with CrossRef metadata (cached + incremental save)
    - Save list_compiled.json/csv
    - Generate search_summary.csv
    """
    print("[INFO] Starting compilation process...")

    # Paths
    RESULTS_DIR = Path("results/search_results")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    compiled_json_file = RESULTS_DIR / "list_compiled.json"
    compiled_csv_file = RESULTS_DIR / "list_compiled.csv"
    crossref_cache_file = RESULTS_DIR / "crossref_cache.json"

    # Load all JSON search results
    search_files = list(RESULTS_DIR.glob("*.json"))
    if not search_files:
        print("[WARNING] No JSON search files found. Exiting.")
        return

    db_entries = {}
    for f in search_files:
        db_name = f.stem
        try:
            print(f"[INFO] Loading database file: {f}")
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    print(f"[WARNING] {f} does not contain a list. Skipping.")
                    continue
                db_entries[db_name] = data
        except Exception as e:
            print(f"[WARNING] Could not read {f}: {e}")

    # Deduplicate
    compiled = []
    seen = {}
    def generate_keys(entry):
        keys = []
        doi = entry.get("doi")
        title = entry.get("title")
        url = entry.get("url")
        if doi: keys.append(f"doi::{doi.strip().lower()}")
        if title: keys.append(f"title::{title.strip().lower()}")
        if url: keys.append(f"url::{url.strip().lower()}")
        return keys

    print("[INFO] Deduplicating entries...")
    for db_name, entries in db_entries.items():
        for entry in entries:
            if "is_referenced_by_count" in entry and "cited_by" not in entry:
                entry["cited_by"] = entry["is_referenced_by_count"]
            entry.setdefault("databases_found_in", [])
            if db_name not in entry["databases_found_in"]:
                entry["databases_found_in"].append(db_name)

            keys = generate_keys(entry)
            found = False
            for key in keys:
                if key in seen:
                    idx = seen[key]
                    compiled_entry = compiled[idx]
                    # Merge metadata
                    for k, v in entry.items():
                        if k == "databases_found_in":
                            compiled_entry[k] = list(set(compiled_entry[k] + v))
                        elif k not in compiled_entry or compiled_entry[k] in (None, "", []):
                            compiled_entry[k] = v
                    found = True
                    break
            if not found:
                idx = len(compiled)
                compiled.append(entry)
                for key in keys:
                    seen[key] = idx

    print(f"[INFO] Deduplication complete. Total unique entries: {len(compiled)}")

    # Enhance with CrossRef metadata
    enhance_compiled_with_crossref(compiled, compiled_json_file, crossref_cache_file)

    # Sort by cited_by
    compiled_sorted = sorted(compiled, key=lambda x: x.get("cited_by", 0) or 0, reverse=True)

    # Save JSON & CSV
    with open(compiled_json_file, "w", encoding="utf-8") as f:
        json.dump(compiled_sorted, f, indent=2, ensure_ascii=False)
    pd.DataFrame(compiled_sorted).to_csv(compiled_csv_file, index=False)
    print(f"[INFO] Compiled data saved: {compiled_json_file}, {compiled_csv_file}")

    # Build search summary CSV
    summary_rows = []
    for db_name, entries in db_entries.items():
        row = {"database": db_name, "num_results": len(entries)}
        if entries:
            fields = sorted({k for e in entries for k in e.keys()})
            row["fields_captured"] = ", ".join(fields)
        else:
            row["fields_captured"] = ""
        # Overlaps
        for other_db_name, other_entries in db_entries.items():
            if db_name == other_db_name:
                row[f"in_{other_db_name}"] = len(entries)
                continue
            other_keys = set(k for e in other_entries for k in generate_keys(e))
            count_overlap = sum(any(k in other_keys for k in generate_keys(e)) for e in entries)
            row[f"in_{other_db_name}"] = count_overlap
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    summary_csv_file = RESULTS_DIR / "search_summary.csv"
    summary_df.to_csv(summary_csv_file, index=False)
    print(f"[INFO] Search summary saved: {summary_csv_file}")
    print("[INFO] Compilation process completed successfully!")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    compile_searches()
