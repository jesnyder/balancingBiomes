#!/usr/bin/env python3
"""
AI Enrichment Script for Google Scholar JSON using CrossRef

Title: Google Scholar to CrossRef Enrichment with DOI + Title Fallback

Objective:
- Enrich Google Scholar JSON with CrossRef metadata.
- Keep all original fields intact.
- Main function must be exactly named `add_crossref_to_gscholar`.

Lessons Learned / Important Notes:
- DOI-based queries are preferred; fallback to cleaned title search if DOI missing.
- Remove HTML tags (<jats:p>) and markers [PDF], [HTML], [BOOK], [B].
- Trim leading/trailing whitespace from all fields.
- Remove line breaks (\n, \r) from titles before CrossRef title search and from abstracts before saving.
- Preserve original fields; add CrossRef metadata: type, container-title, abstract, author, is-referenced-by-count, funder.
- Update `query` key list to include 'crossref' and method used.
- Log successes, failures, missing metadata.
- Throttle queries to 1s to avoid CrossRef overload.
- Sort enriched list by `citations` descending.
- Save enriched JSON and detailed log for reproducibility.
- Save a concise summary of successes/failures to `results/search_results/summary_gscholar_crossref.txt`.
- Must preserve exact instructions to allow reproduction by AI or humans.
- Lesson from previous error: always ensure each article is a dict, not a string. Use lowercase 'doi' to match JSON.

Input:
- JSON: results/search_results/list_gscholar.json
- Each article has fields: title, doi, query, citations, and others

Output:
- JSON: results/search_results/list_gscholar_crossref.json
- Log: results/search_results/list_crossref_gscholar.txt
- Summary: results/search_results/summary_gscholar_crossref.txt
- Prints enrichment summary to terminal

Approach:
1. Load Google Scholar JSON.
2. For each article:
   a. Enrich using DOI first.
   b. If DOI missing, clean Title (remove HTML, markers, line breaks) and search CrossRef.
   c. Add metadata: type, container-title, abstract (cleaned, no line breaks), author, is-referenced-by-count, funder.
   d. Update `query` key list with 'crossref' and method used.
   e. Clean all fields.
   f. Log success/failure.
3. Sort final JSON by citations descending.
4. Save JSON, detailed log, and summary file.
"""

import os
import json
import re
import time
from pathlib import Path
from crossref.restful import Works
from bs4 import BeautifulSoup

GSCHOLAR_JSON = "results/search_results/list_gscholar.json"
OUTPUT_JSON = "results/search_results/list_gscholar_crossref.json"
LOG_FILE = "results/search_results/list_crossref_gscholar.txt"
SUMMARY_FILE = "results/search_results/summary_gscholar_crossref.txt"

works = Works()

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def clean_text(text):
    """Remove HTML tags, markers, line breaks, and trim whitespace."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\[(PDF|HTML|BOOK|B)\]", "", text, flags=re.IGNORECASE)
    text = text.replace("\n", " ").replace("\r", " ").strip()
    return text

def enrich_article(art):
    """Enrich a single article dict with CrossRef metadata."""
    if not isinstance(art, dict):
        return art, "Not a dict"

    doi = art.get("doi", "").strip()
    method_used = ""
    metadata = None

    try:
        if doi:
            metadata = works.doi(doi)
            method_used = "doi"
        else:
            title_clean = clean_text(art.get("title", ""))
            if title_clean:
                results = works.query(title=title_clean).sort("score", "desc").limit(1)
                for res in results:
                    metadata = res
                    method_used = "title"
                    break

        if metadata:
            art["type"] = metadata.get("type", "")
            container = metadata.get("container-title", [])
            art["container-title"] = clean_text(container[0]) if container else ""
            abstract = metadata.get("abstract", "")
            art["abstract"] = clean_text(abstract)  # remove line breaks here too
            art["author"] = metadata.get("author", [])
            art["is-referenced-by-count"] = metadata.get("is-referenced-by-count", 0)
            art["funder"] = metadata.get("funder", [])

            if "query" not in art or not isinstance(art["query"], list):
                art["query"] = []
            if "crossref" not in art["query"]:
                art["query"].append("crossref")
            if method_used not in art["query"]:
                art["query"].append(method_used)

            # Clean all text fields in the article
            for key, value in art.items():
                if isinstance(value, str):
                    art[key] = clean_text(value)

            return art, f"Enriched via {method_used}"
        else:
            return art, "No metadata found"

    except Exception as e:
        return art, f"Error: {e}"

# --------------------------------------------------
# Main Function
# --------------------------------------------------

def add_crossref_to_gscholar():
    print("[MAIN] Loading Google Scholar compiled list...")
    Path(os.path.dirname(OUTPUT_JSON)).mkdir(parents=True, exist_ok=True)
    log_lines = []

    with open(GSCHOLAR_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    enriched_count = 0
    failed_count = 0
    enriched_doi = 0
    enriched_title = 0

    for idx, art in enumerate(articles, start=1):
        art, status = enrich_article(art)
        if "Enriched" in status:
            enriched_count += 1
            if "doi" in status:
                enriched_doi += 1
            elif "title" in status:
                enriched_title += 1
        else:
            failed_count += 1

        log_lines.append(f"[{idx}/{len(articles)}] {art.get('title', 'NO TITLE')} - {status}")
        print(f"[{idx}/{len(articles)}] {art.get('title', 'NO TITLE')} - {status}")

        # Save intermediate JSON after each enrichment for safety
        enriched_data = {"count": len(articles), "articles": articles}
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)

        time.sleep(1)  # throttle queries

    # Sort by citations descending
    articles.sort(key=lambda x: x.get("citations", 0), reverse=True)
    enriched_data = {"count": len(articles), "articles": articles}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)
    print(f"[MAIN] Enriched list saved to {OUTPUT_JSON}")

    # Save log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"[MAIN] Detailed log saved to {LOG_FILE}")

    # Save summary
    summary_text = (
        f"Total Articles: {len(articles)}\n"
        f"Enriched: {enriched_count} (DOI: {enriched_doi}, Title fallback: {enriched_title})\n"
        f"Failed: {failed_count}"
    )
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"[MAIN] Summary saved to {SUMMARY_FILE}")
    print(f"[MAIN] Enriched {enriched_count} (DOI: {enriched_doi}, Title: {enriched_title}), Failed {failed_count}")

# --------------------------------------------------
# Run if executed directly
# --------------------------------------------------

if __name__ == "__main__":
    add_crossref_to_gscholar()
