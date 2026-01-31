#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date generated: 2026-01-31

Objective:
    List articles returned from a Google Scholar search for articles using the query:
    ("Halophytes" AND "Halophile"). Only articles relevant to both terms will be included.
    Search is not case sensitive.

Tasks:
    1. Define the query and URL template for Google Scholar.
    2. Paginate through results, 10 articles per page.
    3. Respect rate limits to avoid IP blocks:
       - Wait 70 seconds between page requests to prevent HTTP 429 responses.
    4. Handle HTTP errors:
       - Stop requests on error codes (429, 503, 403) and continue with remaining tasks.
    5. Parse results:
       - Extract article metadata (title, authors, year, snippet, links, etc.).
    6. Save results:
       - Each page’s results are saved immediately as JSON.
       - File naming includes timestamp and page index.
    7. Logging:
       - Print progress messages to terminal for each step.

Input:
    - Packages: requests, BeautifulSoup4, json, os, time, datetime
    - Internet access to Google Scholar (https://scholar.google.com/)

Output:
    - JSON files for each page of results saved in:
      results/search_results/gscholar/pages/
      Example: 202601311230_0000.json
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

def search_gscholar():
    """
    Main function to search Google Scholar for articles about "Halophytes" AND "Halophile"
    and save each page of results as JSON.
    """

    # -------------------------------
    # Configuration
    # -------------------------------
    query = '"Halophytes" AND "Halophile"'  # Google Scholar search query
    base_url = "https://scholar.google.com/scholar"  # Base URL
    results_per_page = 10  # Google Scholar shows 10 results per page
    max_pages = 5  # Adjust as needed, here just 5 pages for demonstration
    wait_seconds = 70  # Wait time between requests to avoid HTTP 429
    output_dir = "results/search_results/gscholar/pages"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------
    # Loop over pages
    # -------------------------------
    for page in range(max_pages):
        start_index = page * results_per_page  # Google Scholar uses start index for pagination
        print(f"📄 Fetching page {page} (start={start_index})...")

        # -------------------------------
        # Build request parameters
        # -------------------------------
        params = {
            "q": query,         # Query string
            "hl": "en",         # Language: English
            "start": start_index  # Pagination index
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }

        # -------------------------------
        # Send GET request to Google Scholar
        # -------------------------------
        try:
            response = requests.get(base_url, params=params, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request failed: {e}")
            break  # Stop if network error occurs

        # -------------------------------
        # Handle HTTP errors
        # -------------------------------
        if response.status_code == 429:
            print("⚠️ HTTP 429 Too Many Requests - stopping scraping.")
            break
        elif response.status_code in [503, 403]:
            print(f"⚠️ HTTP {response.status_code} Error - possible block detected. Stopping.")
            break
        elif response.status_code != 200:
            print(f"⚠️ HTTP {response.status_code} Error - skipping this page.")
            continue

        # -------------------------------
        # Parse the HTML content
        # -------------------------------
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []

        # Google Scholar lists articles in <div class="gs_ri">
        for div in soup.find_all("div", class_="gs_ri"):
            title_tag = div.find("h3", class_="gs_rt")
            if title_tag:
                # Clean title text
                title = title_tag.get_text()
                # Extract link if available
                link = title_tag.find("a")["href"] if title_tag.find("a") else ""

            author_year_tag = div.find("div", class_="gs_a")
            author_year_text = author_year_tag.get_text() if author_year_tag else ""

            snippet_tag = div.find("div", class_="gs_rs")
            snippet = snippet_tag.get_text() if snippet_tag else ""

            # Build article metadata dictionary
            article = {
                "title": title,
                "link": link,
                "authors_year": author_year_text,
                "snippet": snippet
            }

            articles.append(article)

        # -------------------------------
        # Save page results to JSON
        # -------------------------------
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"{timestamp}_{page:04d}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        print(f"✅ Page {page} saved to {filepath}")
        print(f"🛌 Waiting {wait_seconds} seconds before next request...")
        time.sleep(wait_seconds)

    print("🎯 Google Scholar scraping completed.")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    search_gscholar()
