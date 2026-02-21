# Date Created: 2026-02-18
# Objective: Query Google Scholar for articles containing both "Halophyte" and "Halophile",
#            save each page of results, compile all saved pages after each page, deduplicate,
#            sort by citations, and produce an up-to-date compiled JSON after each page.
# Dependencies: scholarly (Python library for Google Scholar queries), os, json, glob, time, datetime

import os
import json
import glob
import time
from datetime import datetime
from scholarly import scholarly  # scholarly library handles Google Scholar queries

def query_gscholar():
    """
    Main function to query Google Scholar, save each page, compile after each page,
    deduplicate, and finally produce a compiled JSON of all articles.
    """

    # --- Setup ---
    search_query = 'Halophyte AND Halophile'
    max_pages = 500  # Stop after 500 pages
    results_folder = 'results/query/gscholar/pages'
    compiled_file = 'results/query/gscholar/query_gscholar.json'

    os.makedirs(results_folder, exist_ok=True)

    # --- Step 1: Initialize the compiled list ---
    articles = []

    # --- Step 2: Load previously saved pages ---
    saved_pages = sorted(glob.glob(os.path.join(results_folder, '*.json')))
    print(f"Found {len(saved_pages)} previously saved pages. Loading them...")
    for page_file in saved_pages:
        with open(page_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    articles.extend(data)
                elif isinstance(data, dict) and "results" in data:
                    articles.extend(data["results"])
                else:
                    print(f"Warning: Unknown JSON structure in {page_file}")
            except Exception as e:
                print(f"Error loading {page_file}: {e}")
    print(f"Loaded {len(articles)} articles from saved pages.")

    # --- Step 3: Query Google Scholar page by page ---
    search = scholarly.search_pubs(search_query)
    page_count = 0

    while page_count < max_pages:
        try:
            # --- Fetch one page (10 results) ---
            page_articles = []
            for _ in range(10):
                article = next(search, None)
                if article is None:
                    break
                page_articles.append(article)

            if not page_articles:
                print("No more articles returned by Google Scholar.")
                break

            # --- Save the page ---
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            page_file = os.path.join(results_folder, f"{timestamp}_{page_count:04d}.json")
            with open(page_file, 'w', encoding='utf-8') as f:
                json.dump(page_articles, f, ensure_ascii=False, indent=2)
            print(f"Saved page {page_count + 1} with {len(page_articles)} articles.")

            # --- Append to compiled list ---
            articles.extend(page_articles)

            # --- Step 4: Incremental compilation after each page ---
            unique_articles = {}
            for art in articles:
                key = art.get('pub_url') or art.get('title') or str(art)
                unique_articles[key] = art
            articles = list(unique_articles.values())
            articles_sorted = sorted(articles, key=lambda x: x.get('num_citations', 0), reverse=True)

            article_count = len(articles)
            article_count_2 = sum(1 for a in articles if a.get('num_citations', 0) > 2)

            compiled_data = {
                "article_count": article_count,
                "article_count_2": article_count_2,
                "articles": articles_sorted
            }

            with open(compiled_file, 'w', encoding='utf-8') as f:
                json.dump(compiled_data, f, ensure_ascii=False, indent=2)

            print(f"Compiled JSON updated after page {page_count + 1}: {compiled_file} "
                  f"(Total articles: {article_count}, >2 citations: {article_count_2})")

            # --- Prepare for next page ---
            page_count += 1
            time.sleep(65)  # Wait 60 seconds to avoid being blocked

        except Exception as e:
            print(f"Error during Google Scholar query: {e}")
            print("Stopping further requests to avoid being blocked.")
            break

    # --- Step 5: Final compilation ---
    print("Final compilation complete. All pages processed.")
    print(f"Total articles: {len(articles)}, Articles with >2 citations: {article_count_2}")


# --- Run the function ---
if __name__ == "__main__":
    query_gscholar()
