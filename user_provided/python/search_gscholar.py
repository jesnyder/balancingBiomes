import requests
import time
import random
import json
import csv
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

QUERY = '"Halophyte" AND "Halophile"'
BASE_URL = "https://scholar.google.com/scholar"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

RESULTS_PER_PAGE = 10
MAX_PAGES = 3  # adjust as needed

def fetch_page(start):
    params = {
        "q": QUERY,
        "start": start
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for entry in soup.select(".gs_r.gs_or.gs_scl"):
        title_tag = entry.select_one("h3.gs_rt")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        link_tag = title_tag.find("a")
        link = link_tag["href"] if link_tag else None

        citation_tag = entry.select_one(".gs_fl a")
        citations = 0
        if citation_tag and "Cited by" in citation_tag.text:
            try:
                citations = int(citation_tag.text.split()[-1])
            except ValueError:
                citations = 0

        results.append({
            "title": title,
            "link": link,
            "citations": citations
        })

    return results


def search_gscholar():
    all_results = []

    for page in range(MAX_PAGES):
        start = page * RESULTS_PER_PAGE
        print(f"Fetching page {page}...")

        html = fetch_page(start)
        results = parse_results(html)

        page_filename = f"gscholar_{page:04d}.json"
        with open(page_filename, "w") as f:
            json.dump(results, f, indent=2)

        all_re_
