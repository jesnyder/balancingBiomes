import os
import json
import time
import random
import requests
import re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

# ============================================================================
# CONFIGURATION
# ============================================================================
RESULTS_DIR = Path("results/search_results")
GSCHOLAR_PAGES_DIR = RESULTS_DIR / "gscholar" / "pages"
COMPILED_OUTPUT = RESULTS_DIR / "list_gscholar.json"
SEARCH_QUERY = '("Halophyte" AND "Halophile")'

# Create directories if they don't exist
GSCHOLAR_PAGES_DIR.mkdir(parents=True, exist_ok=True)
print(f"[INIT] Created directory structure: {GSCHOLAR_PAGES_DIR}")

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
print(f"[INIT] User-Agent header configured")


def clean_field(text):
    """
    Clean text by removing HTML tags, [HTML], [BOOK], [B], and whitespace.

    Why: Google Scholar includes metadata markers and HTML that needs to be cleaned.
    """
    if not text:
        return text

    # Remove [HTML] marker
    text = re.sub(r'\[HTML\]', '', text)
    # Remove [BOOK] marker
    text = re.sub(r'\[BOOK\]', '', text)
    # Remove [B] marker
    text = re.sub(r'\[B\]', '', text)
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Strip leading and trailing whitespace
    text = text.strip()
    # Remove extra internal whitespace
    text = ' '.join(text.split())

    return text


def clean_articles(articles):
    """
    Clean all text fields in articles.

    Why: Ensures consistent, readable data. Removes formatting noise from web scraping.
    """
    print(f"[CLEAN] Cleaning {len(articles)} articles...")

    fields_to_clean = ['title', 'authors', 'publication', 'url', 'title_link']

    for article in articles:
        for field in fields_to_clean:
            if field in article and article[field]:
                article[field] = clean_field(article[field])

    print(f"[CLEAN] ✓ Complete")
    return articles


def add_required_keys(articles):
    """
    Add required keys to all articles.

    CRITICAL: Do not skip this step.
    - Adds cited_by key (set to citations value)
    - Adds url key (set to title_link value)
    """
    print(f"[KEYS] Adding required keys to {len(articles)} articles...")

    for article in articles:
        # Add cited_by key - must not skip this
        if 'citations' in article and article['citations'] is not None:
            article['cited_by'] = article['citations']
        else:
            article['cited_by'] = 0

        # Add url key - must not skip this
        if 'title_link' in article and article['title_link']:
            article['url'] = article['title_link']
        elif 'url' not in article:
            article['url'] = ''

    print(f"[KEYS] ✓ Complete")
    return articles


def compile_existing_results():
    """
    Load all existing JSON files from gscholar/pages directory.

    Why: Allows scraping sessions to build on previous work without re-scraping.
    """
    articles = []
    print(f"\n[COMPILE] Checking for existing results in: {GSCHOLAR_PAGES_DIR}")

    if not GSCHOLAR_PAGES_DIR.exists():
        print(f"[COMPILE] Directory does not exist - first run")
        return articles

    json_files = sorted(GSCHOLAR_PAGES_DIR.glob("*.json"))
    print(f"[COMPILE] Found {len(json_files)} existing JSON files")

    if not json_files:
        return articles

    for json_file in json_files:
        try:
            print(f"[COMPILE] Loading: {json_file.name}...", end=" ")
            with open(json_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)

                # Look for "results" key
                if isinstance(file_data, dict) and 'results' in file_data:
                    page_articles = file_data['results']
                    if isinstance(page_articles, list):
                        articles.extend(page_articles)
                        print(f"✓ Found {len(page_articles)} articles")
                    else:
                        print(f"⚠ 'results' not a list")
                # Fallback to direct list format
                elif isinstance(file_data, list):
                    articles.extend(file_data)
                    print(f"✓ Found {len(file_data)} articles")
                else:
                    print(f"⚠ Unrecognized format")

        except json.JSONDecodeError:
            print(f"❌ Invalid JSON")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print(f"[COMPILE] ✓ Total: {len(articles)} articles loaded")
    return articles


def parse_gscholar_page(html_content, page_num):
    """
    Parse Google Scholar HTML and extract article information.

    Extracts: title, title_link, authors, publication, year, citations, doi.
    """
    articles = []
    print(f"\n[PARSE {page_num:04d}] Parsing HTML ({len(html_content):,} chars)...")

    soup = BeautifulSoup(html_content, 'html.parser')

    # Google Scholar stores results in divs with class 'gs_ri'
    results = soup.find_all('div', class_='gs_ri')
    print(f"[PARSE {page_num:04d}] Found {len(results)} article containers")

    for idx, result in enumerate(results):
        try:
            article = {}

            # Extract title and title_link
            title_elem = result.find('h3', class_='gs_ct')
            if title_elem and title_elem.find('a'):
                article['title'] = title_elem.find('a').get_text()
                article['title_link'] = title_elem.find('a').get('href', '')
            else:
                continue

            # Extract authors, publication, year
            info_elem = result.find('div', class_='gs_a')
            if info_elem:
                text = info_elem.get_text()
                parts = [p.strip() for p in text.split(' - ')]
                article['authors'] = parts[0] if len(parts) > 0 else ''
                article['publication'] = parts[1] if len(parts) > 1 else ''
                article['year'] = parts[2] if len(parts) > 2 else ''

            # Extract citation count
            article['citations'] = None
            cite_elem = result.find('a', string=lambda s: s and 'Cited by' in s)
            if cite_elem:
                try:
                    cite_text = cite_elem.get_text()
                    cite_count = int(cite_text.split()[-1])
                    article['citations'] = cite_count
                except (ValueError, IndexError):
                    pass

            # Extract DOI if present
            article['doi'] = None
            links = result.find_all('a')
            for link in links:
                href = link.get('href', '')
                if 'doi.org' in href:
                    article['doi'] = href.split('/')[-1]
                    break

            articles.append(article)

        except Exception as e:
            print(f"[PARSE {page_num:04d}] Error parsing article {idx+1}: {str(e)}")
            continue

    print(f"[PARSE {page_num:04d}] ✓ Successfully parsed {len(articles)} articles")
    return articles


def deduplicate_articles(articles):
    """
    Remove duplicate articles using DOI and URL as unique identifiers.

    Why: Same article may appear on multiple pages. DOI is globally unique.
    """
    seen = set()
    deduplicated = []
    duplicates_removed = 0

    print(f"\n[DEDUP] Processing {len(articles):,} articles...")

    for article in articles:
        # Create unique identifier from DOI, URL, or title
        unique_id = None

        if article.get('doi'):
            unique_id = ('doi', article['doi'])
        elif article.get('url') or article.get('title_link'):
            # Use url if available, otherwise title_link
            unique_id = ('url', article.get('url') or article.get('title_link'))
        else:
            unique_id = ('title', article.get('title', ''))

        if unique_id not in seen:
            seen.add(unique_id)
            deduplicated.append(article)
        else:
            duplicates_removed += 1

    print(f"[DEDUP] ✓ Removed {duplicates_removed} duplicates")
    print(f"[DEDUP] ✓ Final count: {len(deduplicated)} unique articles")
    return deduplicated


def sort_by_citations(articles):
    """
    Sort articles by citation count (highest first).

    Why: Most cited articles are usually most influential. Helps identify key papers.
    """
    print(f"\n[SORT] Sorting {len(articles):,} articles...")

    with_citations = [a for a in articles if a.get('citations') is not None]
    without_citations = [a for a in articles if a.get('citations') is None]

    print(f"[SORT] Articles with citations: {len(with_citations):,}")
    print(f"[SORT] Articles without citations: {len(without_citations):,}")

    # Sort by citations in descending order (highest first)
    with_citations.sort(key=lambda x: x['citations'], reverse=True)

    sorted_result = with_citations + without_citations
    print(f"[SORT] ✓ Complete: {len(sorted_result):,} articles sorted")

    return sorted_result


def compile_and_save():
    """
    Helper function to compile, clean, deduplicate, sort, and save results.

    This is called:
    1. At the start (before scraping)
    2. After each page is scraped
    3. At the end

    This ensures continuous updating of the compiled results.
    """
    print(f"\n{'='*100}")
    print("[COMPILE_AND_SAVE] Running full compilation pipeline")
    print(f"{'='*100}")

    # Step 1: Compile existing results
    compiled_articles = compile_existing_results()

    # Step 2: Clean articles
    compiled_articles = clean_articles(compiled_articles)

    # Step 3: Add required keys
    compiled_articles = add_required_keys(compiled_articles)

    # Step 4: Deduplicate
    compiled_articles = deduplicate_articles(compiled_articles)

    # Step 5: Sort by citations
    compiled_articles = sort_by_citations(compiled_articles)

    # Step 6: Save to file
    print(f"\n[SAVE] Saving {len(compiled_articles)} articles to: {COMPILED_OUTPUT}")

    with open(COMPILED_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(compiled_articles, f, indent=2, ensure_ascii=False)
    print(f"[SAVE] ✓ Successfully saved")

    # Verify file
    if os.path.exists(COMPILED_OUTPUT):
        file_size = os.path.getsize(COMPILED_OUTPUT)
        print(f"[SAVE] File size: {file_size:,} bytes")
        print(f"[SAVE] Total articles: {len(compiled_articles)}")

        # Verify keys
        articles_with_cited_by = sum(1 for a in compiled_articles if 'cited_by' in a)
        articles_with_url = sum(1 for a in compiled_articles if 'url' in a)
        print(f"[SAVE] Articles with cited_by: {articles_with_cited_by}/{len(compiled_articles)}")
        print(f"[SAVE] Articles with url: {articles_with_url}/{len(compiled_articles)}")

        if articles_with_cited_by != len(compiled_articles) or articles_with_url != len(compiled_articles):
            print(f"[SAVE] ⚠ WARNING: Missing required keys on some articles!")
    else:
        print(f"[SAVE] ❌ ERROR: File was not saved!")

    return compiled_articles


def search_gscholar(query=SEARCH_QUERY, max_pages=None):
    """
    Main function to scrape Google Scholar.

    Workflow:
    1. Compile results, clean, and save (initial)
    2. Query ("Halophyte" AND "Halophile")
    3. For each page:
       a. Wait 60 + random(0-20) seconds
       b. Fetch page
       c. Parse articles
       d. Save page to JSON with "results" key
       e. Compile all results, clean, deduplicate, sort, and save
    4. Stop on error or end of results
    """

    print("\n" + "="*100)
    print("[STEP 0] INITIAL COMPILATION AND SAVE")
    print("="*100)
    # Compile, clean, and save existing results before scraping
    compile_and_save()

    print("\n" + "="*100)
    print("[STEP 1] STARTING NEW GOOGLE SCHOLAR SEARCH")
    print("="*100)
    print(f"[SEARCH] Query: {query}")
    print(f"[SEARCH] Max pages: {max_pages if max_pages else 'unlimited'}")
    print(f"[SEARCH] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    page_num = 0
    consecutive_errors = 0
    max_consecutive_errors = 3

    # Main scraping loop
    while True:
        print(f"\n{'─'*100}")
        print(f"[PAGE {page_num:04d}] Starting page {page_num}...")
        print(f"{'─'*100}")

        # Check page limit
        if max_pages and page_num >= max_pages:
            print(f"[PAGE {page_num:04d}] Max pages reached ({max_pages}). Stopping.")
            break

        try:
            # Wait between requests (60 + random 0-20 seconds)
            # This delay makes scraper look like human browsing
            wait_time = 60 + random.randint(0, 20)
            print(f"[PAGE {page_num:04d}] Waiting {wait_time} seconds...")
            for i in range(wait_time):
                if i % 10 == 0 and i > 0:
                    print(f"[PAGE {page_num:04d}]   ...{wait_time - i} seconds remaining")
                time.sleep(1)

            # Build URL with pagination
            # Google Scholar: start parameter controls pagination (0, 10, 20, etc.)
            start_param = page_num * 10
            url = f"https://scholar.google.com/scholar?q={quote(query)}&start={start_param}"

            print(f"\n[PAGE {page_num:04d}] Fetching: {url}")

            # Fetch page from Google Scholar
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            print(f"[PAGE {page_num:04d}] ✓ HTTP {response.status_code}")
            print(f"[PAGE {page_num:04d}] ✓ Response: {len(response.text):,} characters")

            # Parse HTML to extract articles
            articles = parse_gscholar_page(response.text, page_num)

            # Stop if no articles found (end of results)
            if not articles:
                print(f"[PAGE {page_num:04d}] No articles found - end of results")
                break

            # Save this page to JSON file with "results" key
            page_data = {"results": articles}
            page_filename = GSCHOLAR_PAGES_DIR / f"{page_num:04d}_gscholar.json"
            with open(page_filename, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            print(f"[PAGE {page_num:04d}] ✓ Saved page to {page_filename}")

            # Show sample
            print(f"[PAGE {page_num:04d}] Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                title = article.get('title', 'N/A')[:70]
                citations = article.get('citations', 'Unknown')
                print(f"[PAGE {page_num:04d}]   {i}. {title}... ({citations})")

            # CRITICAL: After each page, re-compile, clean, and save results
            # This ensures continuous updating of the compiled file
            print(f"\n[PAGE {page_num:04d}] Re-compiling results after page scrape...")
            compile_and_save()

            # Reset error counter on success
            consecutive_errors = 0
            page_num += 1

        except requests.exceptions.Timeout:
            consecutive_errors += 1
            print(f"\n[PAGE {page_num:04d}] ❌ TIMEOUT ERROR - Request took too long")
            print(f"[PAGE {page_num:04d}] Errors: {consecutive_errors}/{max_consecutive_errors}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"[PAGE {page_num:04d}] Max errors reached. Stopping and compiling results.")
                break

        except requests.exceptions.ConnectionError as e:
            consecutive_errors += 1
            print(f"\n[PAGE {page_num:04d}] ❌ CONNECTION ERROR: {str(e)}")
            print(f"[PAGE {page_num:04d}] Errors: {consecutive_errors}/{max_consecutive_errors}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"[PAGE {page_num:04d}] Max errors reached. Stopping and compiling results.")
                break

        except requests.exceptions.HTTPError as e:
            consecutive_errors += 1
            print(f"\n[PAGE {page_num:04d}] ❌ HTTP ERROR: {str(e)}")
            print(f"[PAGE {page_num:04d}] Errors: {consecutive_errors}/{max_consecutive_errors}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"[PAGE {page_num:04d}] Max errors reached. Stopping and compiling results.")
                break

        except Exception as e:
            consecutive_errors += 1
            print(f"\n[PAGE {page_num:04d}] ❌ ERROR: {str(e)}")
            print(f"[PAGE {page_num:04d}] Type: {type(e).__name__}")
            print(f"[PAGE {page_num:04d}] Errors: {consecutive_errors}/{max_consecutive_errors}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"[PAGE {page_num:04d}] Max errors reached. Stopping and compiling results.")
                break

    print("\n" + "="*100)
    print("[FINAL] FINAL COMPILATION AND SAVE")
    print("="*100)
    # Final compile and save after all scraping is done
    final_results = compile_and_save()

    return final_results


if __name__ == "__main__":
    print("\n" + "="*100)
    print("GOOGLE SCHOLAR SCRAPER - STARTING")
    print("="*100)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Script location: {os.path.abspath(__file__)}")

    try:
        # Run the main search function
        results = search_gscholar()

        print("\n" + "="*100)
        print("GOOGLE SCHOLAR SCRAPER - COMPLETE")
        print("="*100)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total articles: {len(results):,}")
        print(f"Output file: {os.path.abspath(COMPILED_OUTPUT)}")
        print("="*100 + "\n")

    except KeyboardInterrupt:
        print("\n\n[ERROR] ❌ Script interrupted by user (Ctrl+C)")
        print("[ERROR] Running final compilation to save progress...")
        compile_and_save()

    except Exception as e:
        print(f"\n\n[ERROR] ❌ Critical error: {str(e)}")
        print(f"[ERROR] Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
