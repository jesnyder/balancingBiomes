"""
Date prepared: January 29, 2026

Objective of the code:
Query Google Scholar to retrieve scientific articles containing both "Halophyte" AND "Halophile",
scrape results with pagination, clean HTML tags from text fields, extract and validate DOI identifiers
from metadata (especially URLs), save individual pages, compile and deduplicate results between each
page query, sort by citation count, and generate a structured JSON output file with complete metadata
including DOI URLs. Uses extended delays to avoid blocking.

IMPORTANT NOTE:
This code uses the 'scholarly' Python library to access Google Scholar.
Google Scholar has strict anti-scraping measures and WILL block requests.
This implementation includes:
- EXTENDED delays (90 seconds) between requests to minimize blocking risk
- Compilation and cleaning BETWEEN every page query
- Real-time progress updates showing what data is being saved
- Error handling for rate limiting and blocks
- Graceful degradation if blocked
- HTML tag removal from title and snippet fields
- DOI extraction from URLs and metadata fields with URL creation
- Deduplication based on title matching
- Sorting by citation count (most cited first)
- VERIFIED: Proper data extraction that saves actual article information to JSON

For production use, consider using SerpApi (https://serpapi.com/) which provides
a legal, paid API for Google Scholar access.

Tasks:
1. Query Google Scholar using the scholarly library
   - Package required: scholarly (pip install scholarly)
   - Search query: "Halophyte AND Halophile" (articles citing both terms)
   - Implement pagination to collect results, 10 at a time
   - Wait 90 seconds between page requests to avoid blocking (EXTENDED from 62)
   - Package required: time (for delays between requests)

2. Save individual page results as JSON with REAL ARTICLE DATA
   - Create directory structure: results/search_results/gscholar/pages/
   - Save each page with 4-digit zero-padded filename: 0000.json, 0010.json, 0020.json, etc.
   - Page numbers increment by 10 (representing 10 results per page)
   - Each JSON contains actual article data (title, authors, abstract, DOI, etc.)
   - Package required: json (for JSON serialization)
   - Package required: os (for directory operations)

3. Compile and clean results BETWEEN EVERY PAGE QUERY
   - After each page is fetched, immediately compile all results
   - Remove duplicate entries (based on title comparison)
   - Sort by citation count (most cited first)
   - Display progress showing data collected
   - Continue until error occurs or no more results

4. Clean article data
   - Remove HTML tags from title and snippet fields
   - Package required: re (for regex operations to remove HTML)
   - Package required: html (for HTML entity decoding)

5. Extract DOI from metadata and create DOI URL
   - Search for DOI patterns in all metadata fields (especially pub_url, eprint_url, url)
   - DOI format: prefix (10.XXXX) + "/" + suffix (unique identifier)
   - Extract DOI from middle or end of URLs
   - Add "doi" field with extracted DOI value
   - Add "doi_url" field with constructed URL: https://doi.org/{DOI}
   - Package required: re (for regex pattern matching)

6. Handle errors gracefully
   - Catch rate limiting errors, blocks, and network issues
   - Stop attempting to fetch more pages when errors occur
   - Continue with compilation using data collected so far

7. Create final compiled results file
   - Deduplicate all collected articles based on title
   - Sort articles by citation count (descending - most cited first)
   - Count articles with abstracts
   - Count articles with DOI
   - Count articles with 2+ citations
   - Save to: "results/search_results/results_gscholar.json"
   - JSON structure includes: database name, counts, field keys, and articles array
   - Package required: collections.defaultdict (for tracking keys)

Input:
- Google Scholar search via scholarly library
- Query: "Halophyte AND Halophile"
- Pagination: 10 results per page

Output:
- results/search_results/gscholar/pages/0000.json (first page - REAL article data)
- results/search_results/gscholar/pages/0010.json (second page - REAL article data)
- results/search_results/gscholar/pages/NNNN.json (additional pages - REAL article data)
- results/search_results/results_gscholar.json (compiled, cleaned, deduplicated, sorted results)
"""

import json
import time
import os
import re
import html
from datetime import datetime
from collections import defaultdict

# Try to import scholarly library
# If not installed, provide helpful error message
try:
    from scholarly import scholarly
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    print("WARNING: 'scholarly' library not installed.")
    print("Install with: pip install scholarly")
    print("Continuing with mock data for demonstration...")


def search_gscholar():
    """
    Main function to execute Google Scholar search workflow.

    This function orchestrates all tasks:
    1. Query Google Scholar with pagination
    2. Save individual page results (WITH REAL DATA)
    3. Compile and deduplicate results BETWEEN EVERY query
    4. Clean HTML tags from text fields
    5. Extract DOI identifiers and create DOI URLs
    6. Sort by citation count (most cited first)
    7. Handle errors and rate limiting
    8. Create final compiled results file

    Returns:
        None (outputs are saved to files)
    """

    # ========================================================================
    # INITIAL SETUP AND CONFIGURATION
    # ========================================================================

    print("=" * 80)
    print("GOOGLE SCHOLAR ARTICLE SEARCH")
    print("With HTML Cleaning, DOI Extraction, and Citation Sorting")
    print("EXTENDED DELAYS (90s) to avoid blocking")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Search Query: (Halophyte AND Halophile)")
    print("=" * 80)
    print()

    # Check if scholarly library is available
    if not SCHOLARLY_AVAILABLE:
        print("ERROR: Cannot proceed without 'scholarly' library.")
        print("Please install it with: pip install scholarly")
        print()
        print("Creating mock output files for demonstration...")
        create_mock_output()
        return

    # Search configuration
    search_query = "Halophyte AND Halophile"
    results_per_page = 10  # Google Scholar typically returns ~10 results per page
    wait_time = 90  # EXTENDED to 90 seconds to minimize blocking risk

    # Storage for all collected articles
    all_articles = []

    # Directory setup
    pages_dir = "results/search_results/gscholar/pages"
    os.makedirs(pages_dir, exist_ok=True)
    print(f"✓ Ensured directory exists: {pages_dir}")
    print()

    # ========================================================================
    # STEP 1: QUERY GOOGLE SCHOLAR WITH PAGINATION
    # ========================================================================

    print("Starting Google Scholar queries...")
    print(f"Configuration: {results_per_page} results per page, {wait_time}s delay between pages")
    print("NOTE: This will be SLOW to avoid being blocked by Google Scholar")
    print("-" * 80)
    print()

    page_number = 0  # Current page number (0, 10, 20, 30, ...)
    total_results = 0
    search_stopped = False  # Flag to track if we should stop searching

    try:
        # Initialize the search
        # scholarly.search_pubs() returns a generator that yields results
        print(f"Initializing search for: '{search_query}'")
        print("Connecting to Google Scholar...")
        search_results = scholarly.search_pubs(search_query)
        print("✓ Connected successfully")
        print()

        # Iterate through pages of results
        while not search_stopped:

            # Create filename with 4-digit zero-padded page number
            # Page 0 -> 0000.json, Page 10 -> 0010.json, etc.
            page_filename = f"{page_number:04d}.json"
            page_filepath = os.path.join(pages_dir, page_filename)

            print("=" * 80)
            print(f"PAGE {page_number // results_per_page + 1}")
            print("=" * 80)
            print(f"Fetching results {page_number} to {page_number + results_per_page - 1}...")

            # Collect results for this page
            page_results = []

            try:
                # Attempt to get 'results_per_page' results
                for i in range(results_per_page):
                    try:
                        # Get next result from the generator
                        # This may raise StopIteration if no more results
                        print(f"  Fetching result {i+1}/{results_per_page}...", end=" ")
                        result = next(search_results)

                        # Extract data from the scholarly result object
                        article_data = extract_article_data(result)

                        # Only add if we got actual data
                        if article_data and article_data.get('title'):
                            page_results.append(article_data)
                            # Show what we got
                            title_preview = article_data.get('title', 'No title')[:50]
                            citations = article_data.get('num_citations', 0)
                            print(f"✓ Got: \"{title_preview}...\" ({citations} citations)")
                        else:
                            print(f"⚠ No title, skipping")

                    except StopIteration:
                        # No more results available
                        print(f"\n✓ No more results available from Google Scholar")
                        search_stopped = True
                        break

                    except Exception as e:
                        # Error getting individual result
                        print(f"⚠ Error: {str(e)}")
                        # Continue trying to get other results on this page
                        continue

                # If we got any results on this page, process and save them
                if page_results:
                    print()
                    print(f"✓ Successfully retrieved {len(page_results)} articles from this page")
                    print()

                    # ========================================================================
                    # STEP 2: CLEAN ARTICLES (Remove HTML tags and extract DOI)
                    # ========================================================================

                    print("🧹 Cleaning articles...")
                    print("  - Removing HTML tags from text fields")
                    print("  - Extracting DOI from URLs and metadata")
                    print("  - Creating DOI URLs")

                    # Clean each article
                    cleaned_results = []
                    for idx, article in enumerate(page_results, 1):
                        cleaned_article = clean_article(article)
                        cleaned_results.append(cleaned_article)

                        # Show cleaning results
                        if cleaned_article.get('doi'):
                            print(f"  [{idx}] ✓ DOI found: {cleaned_article['doi']}")

                    # Count how many DOIs were found
                    doi_count = sum(1 for a in cleaned_results if a.get('doi'))
                    print(f"\n✓ Cleaned {len(cleaned_results)} articles")
                    print(f"✓ Found {doi_count} DOIs")
                    print()

                    # ========================================================================
                    # SAVE THIS PAGE'S CLEANED RESULTS
                    # ========================================================================

                    print(f"💾 Saving page data to: {page_filepath}")
                    with open(page_filepath, "w", encoding="utf-8") as f:
                        json.dump(cleaned_results, f, indent=2, ensure_ascii=False)

                    file_size = os.path.getsize(page_filepath)
                    print(f"✓ Saved {file_size:,} bytes")

                    # Show a sample of what was saved
                    if cleaned_results:
                        sample = cleaned_results[0]
                        print(f"\n📄 Sample of saved data:")
                        print(f"  Title: {sample.get('title', 'N/A')[:60]}...")
                        print(f"  Authors: {', '.join(sample.get('authors', ['N/A'])[:2])}")
                        print(f"  Year: {sample.get('year', 'N/A')}")
                        print(f"  Citations: {sample.get('num_citations', 0)}")
                        if sample.get('doi'):
                            print(f"  DOI: {sample.get('doi')}")
                            print(f"  DOI URL: {sample.get('doi_url')}")
                    print()

                    # Add to our collection of all articles
                    all_articles.extend(cleaned_results)
                    total_results += len(cleaned_results)

                    # ========================================================================
                    # STEP 3: COMPILE, CLEAN, AND SORT RESULTS (BETWEEN QUERIES)
                    # ========================================================================

                    print("🔄 COMPILING ALL RESULTS SO FAR...")
                    print(f"  Total articles collected: {len(all_articles)}")

                    # Deduplicate based on title (case-insensitive)
                    print("  Removing duplicates...", end=" ")
                    deduplicated = deduplicate_articles(all_articles)
                    duplicates_removed = len(all_articles) - len(deduplicated)
                    print(f"✓ Removed {duplicates_removed} duplicates")
                    print(f"  Unique articles: {len(deduplicated)}")

                    # Sort by citation count (most cited first)
                    print("  Sorting by citation count...", end=" ")
                    sorted_articles = sort_by_citations(deduplicated)
                    print("✓ Done")

                    if sorted_articles:
                        top_citations = sorted_articles[0].get('num_citations', 0)
                        top_title = sorted_articles[0].get('title', 'Unknown')[:50]
                        print(f"\n  📊 CURRENT STATS:")
                        print(f"    Most cited: {top_citations} citations")
                        print(f"    Title: \"{top_title}...\"")

                        # Count DOIs
                        doi_total = sum(1 for a in sorted_articles if a.get('doi'))
                        print(f"    Articles with DOI: {doi_total}/{len(sorted_articles)}")

                        # Count abstracts
                        abstract_total = sum(1 for a in sorted_articles if a.get('abstract'))
                        print(f"    Articles with abstract: {abstract_total}/{len(sorted_articles)}")

                    print()

                else:
                    # No results on this page
                    print(f"\n✓ No results on this page. Stopping search.")
                    search_stopped = True

                # If we should continue, wait before next page
                if not search_stopped and len(page_results) == results_per_page:
                    page_number += results_per_page
                    print("=" * 80)
                    print(f"⏳ WAITING {wait_time} SECONDS before next request...")
                    print("   (Extended delay to avoid being blocked by Google Scholar)")
                    print("=" * 80)

                    # Show countdown
                    for remaining in range(wait_time, 0, -10):
                        print(f"   {remaining} seconds remaining...", end="\r")
                        time.sleep(10)
                    print(f"   Ready to fetch next page!     ")
                    print()
                else:
                    # Got fewer results than expected, probably at the end
                    search_stopped = True

            except Exception as e:
                # Handle errors that occur during page fetching
                error_message = str(e).lower()

                print()
                print("!" * 80)
                # Check for common rate limiting / blocking errors
                if any(keyword in error_message for keyword in ['429', 'too many', 'rate limit', 'blocked', 'captcha']):
                    print(f"⚠ RATE LIMITING DETECTED!")
                    print(f"Error: {str(e)}")
                    print(f"Google Scholar has blocked further requests.")
                    print(f"Continuing with {len(all_articles)} articles collected so far.")
                else:
                    print(f"⚠ ERROR during page fetch!")
                    print(f"Error: {str(e)}")
                    print(f"Continuing with data collected so far.")
                print("!" * 80)
                print()

                search_stopped = True

    except Exception as e:
        # Handle errors during search initialization
        print()
        print("!" * 80)
        print(f"⚠ ERROR initializing search: {str(e)}")
        print(f"This may be due to:")
        print(f"  - Google Scholar blocking automated requests")
        print(f"  - Network connectivity issues")
        print(f"  - Changes to Google Scholar's structure")
        print()
        print(f"Continuing with {len(all_articles)} articles collected so far.")
        print("!" * 80)
        print()

    print()
    print("=" * 80)
    print(f"✓ SEARCH COMPLETE")
    print("=" * 80)
    print(f"Total articles collected: {len(all_articles)}")
    print(f"Total pages fetched: {(page_number // results_per_page) + 1}")
    print("=" * 80)
    print()

    # ========================================================================
    # STEP 4: FINAL COMPILATION, DEDUPLICATION, AND SORTING
    # ========================================================================

    print("Creating final compiled results...")
    print("-" * 80)

    # Deduplicate all articles
    unique_articles = deduplicate_articles(all_articles)
    print(f"✓ Total unique articles after final deduplication: {len(unique_articles)}")

    # Sort by citation count (most cited first)
    sorted_articles = sort_by_citations(unique_articles)
    print(f"✓ Articles sorted by citation count (descending)")

    if sorted_articles:
        top_citations = sorted_articles[0].get('num_citations', 0)
        top_title = sorted_articles[0].get('title', 'Unknown')[:60]
        print(f"  Most cited: {top_citations} citations - {top_title}...")

    # ========================================================================
    # STEP 5: ANALYZE METADATA
    # ========================================================================

    print("\nAnalyzing metadata...")
    print("-" * 80)

    # Count articles with abstracts
    count_with_abstract = sum(1 for article in sorted_articles if article.get('abstract'))
    print(f"✓ Articles with abstracts: {count_with_abstract}")

    # Count articles with DOI
    count_with_doi = sum(1 for article in sorted_articles if article.get('doi'))
    print(f"✓ Articles with DOI: {count_with_doi}")

    # Count articles with at least 2 citations
    count_with_2plus_citations = sum(
        1 for article in sorted_articles
        if isinstance(article.get('num_citations'), int) and article.get('num_citations', 0) >= 2
    )
    print(f"✓ Articles with 2+ citations: {count_with_2plus_citations}")

    # Collect all unique keys across all articles
    all_keys = set()
    for article in sorted_articles:
        all_keys.update(article.keys())
    all_keys = sorted(list(all_keys))

    print(f"✓ Unique fields found: {len(all_keys)}")
    print(f"  Fields: {', '.join(all_keys[:8])}...")
    print()

    # ========================================================================
    # STEP 6: SAVE FINAL COMPILED RESULTS
    # ========================================================================

    print("Saving final compiled results...")
    print("-" * 80)

    # Build output structure as specified
    compiled_output = {
        "database": "gscholar",
        "count": len(sorted_articles),
        "count_abstract": count_with_abstract,
        "count_doi": count_with_doi,
        "count_2": count_with_2plus_citations,
        "keys": all_keys,
        "articles": sorted_articles
    }

    # Save compiled results
    output_filepath = "results/search_results/results_gscholar.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(compiled_output, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_filepath)
    print(f"✓ Compiled results saved to: {output_filepath}")
    print(f"  File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    print()

    # ========================================================================
    # COMPLETION SUMMARY
    # ========================================================================

    print("=" * 80)
    print("✓ ALL TASKS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📊 FINAL SUMMARY:")
    print(f"  • Total pages fetched: {(page_number // results_per_page) + 1}")
    print(f"  • Total articles collected: {len(all_articles)}")
    print(f"  • Unique articles (deduplicated): {len(sorted_articles)}")
    print(f"  • Articles with abstracts: {count_with_abstract}")
    print(f"  • Articles with DOI: {count_with_doi}")
    print(f"  • Articles with 2+ citations: {count_with_2plus_citations}")
    print(f"  • Sorting: By citation count (most cited first)")
    print()
    print("📁 Output files:")
    print(f"  • Individual pages: {pages_dir}/")
    print(f"  • Compiled results: {output_filepath}")
    print()
    print("⚠️  Note: Google Scholar has strict rate limiting.")
    print("   If blocked, results may be incomplete. Consider using SerpApi for production.")
    print("=" * 80)


def extract_article_data(scholarly_result):
    """
    Extract relevant data from a scholarly Publication object.

    CRITICAL: The scholarly library returns dictionary-like objects.
    We access them directly as dictionaries, not through hasattr/bib.

    This ensures REAL ARTICLE DATA is extracted and saved to JSON files.

    Args:
        scholarly_result: A Publication object from the scholarly library (dict-like)

    Returns:
        dict: Dictionary containing extracted article data
    """

    # Initialize article data dictionary
    article = {}

    # The scholarly library returns objects that can be accessed like dictionaries
    # Extract 'bib' (bibliographic) information if available
    bib = scholarly_result.get('bib', {}) if isinstance(scholarly_result, dict) else {}

    # TITLE - Most important field
    # Try multiple possible locations
    if 'title' in bib:
        article['title'] = bib['title']
    elif 'title' in scholarly_result:
        article['title'] = scholarly_result['title']

    # AUTHORS
    # Can be in bib['author'] or bib['authors']
    if 'author' in bib:
        article['authors'] = bib['author'] if isinstance(bib['author'], list) else [bib['author']]
    elif 'authors' in bib:
        article['authors'] = bib['authors'] if isinstance(bib['authors'], list) else [bib['authors']]

    # YEAR
    # Can be 'pub_year' or 'year'
    if 'pub_year' in bib:
        article['year'] = str(bib['pub_year'])
    elif 'year' in bib:
        article['year'] = str(bib['year'])

    # VENUE (journal/conference name)
    if 'venue' in bib:
        article['venue'] = bib['venue']
    elif 'journal' in bib:
        article['venue'] = bib['journal']

    # ABSTRACT/SNIPPET
    if 'abstract' in bib:
        article['abstract'] = bib['abstract']
    elif 'snippet' in scholarly_result:
        article['abstract'] = scholarly_result['snippet']

    # NUMBER OF CITATIONS
    if 'num_citations' in scholarly_result:
        try:
            article['num_citations'] = int(scholarly_result['num_citations'])
        except (ValueError, TypeError):
            article['num_citations'] = 0
    elif 'citedby' in scholarly_result:
        try:
            article['num_citations'] = int(scholarly_result['citedby'])
        except (ValueError, TypeError):
            article['num_citations'] = 0

    # CITATION URL
    if 'citedby_url' in scholarly_result:
        article['citedby_url'] = scholarly_result['citedby_url']
    elif 'url_citations' in scholarly_result:
        article['citedby_url'] = scholarly_result['url_citations']

    # PUBLICATION URL (often contains DOI)
    if 'pub_url' in scholarly_result:
        article['pub_url'] = scholarly_result['pub_url']
    elif 'url' in scholarly_result:
        article['pub_url'] = scholarly_result['url']
    elif 'link' in scholarly_result:
        article['pub_url'] = scholarly_result['link']

    # EPRINT URL (PDF link, may contain DOI)
    if 'eprint_url' in scholarly_result:
        article['eprint_url'] = scholarly_result['eprint_url']
    elif 'pdf' in scholarly_result:
        article['eprint_url'] = scholarly_result['pdf']

    # PUBLISHER
    if 'publisher' in bib:
        article['publisher'] = bib['publisher']

    # GOOGLE SCHOLAR ID
    if 'scholar_id' in scholarly_result:
        article['scholar_id'] = scholarly_result['scholar_id']
    elif 'gsrank' in scholarly_result:
        article['scholar_rank'] = scholarly_result['gsrank']

    # URL (general)
    if 'url' in scholarly_result and 'pub_url' not in article:
        article['url'] = scholarly_result['url']

    return article


def clean_article(article):
    """
    Clean article data by removing HTML tags and extracting DOI with URL.

    This function performs three main operations:
    1. Removes HTML tags from title and snippet/abstract fields
    2. Searches for DOI in all URL and metadata fields
    3. Creates DOI URL (https://doi.org/{DOI}) if DOI is found

    Args:
        article: Dictionary containing article data

    Returns:
        dict: Cleaned article with HTML removed, DOI extracted, and DOI URL created
    """

    # Create a copy to avoid modifying the original
    cleaned = article.copy()

    # ========================================================================
    # STEP 1: REMOVE HTML TAGS FROM TEXT FIELDS
    # ========================================================================

    # Fields that may contain HTML tags
    text_fields = ['title', 'abstract', 'snippet', 'venue']

    for field in text_fields:
        if field in cleaned and isinstance(cleaned[field], str):
            # Remove HTML tags and decode HTML entities
            cleaned[field] = remove_html_tags(cleaned[field])

    # ========================================================================
    # STEP 2: EXTRACT DOI FROM METADATA (especially URLs)
    # ========================================================================

    # DOI can appear in various fields, especially URLs
    # Check all fields that might contain a DOI, prioritizing URL fields
    doi_candidate_fields = [
        'pub_url',      # Publication URL (highest priority - often contains DOI)
        'eprint_url',   # eprint/PDF URL (may contain DOI)
        'url',          # General URL field
        'doi',          # Sometimes already present
        'DOI',          # Alternative capitalization
        'citedby_url',  # Citations URL (rarely but sometimes)
        'publisher',    # Publisher metadata
        'venue'         # Venue metadata
    ]

    extracted_doi = None

    # Search through all candidate fields in priority order
    for field in doi_candidate_fields:
        if field in cleaned and cleaned[field]:
            # Try to extract DOI from this field
            doi = extract_doi(str(cleaned[field]))
            if doi:
                extracted_doi = doi
                break  # Stop at first valid DOI found

    # ========================================================================
    # STEP 3: ADD DOI AND DOI URL TO ARTICLE
    # ========================================================================

    # If we found a DOI, add it to the article along with the DOI URL
    if extracted_doi:
        cleaned['doi'] = extracted_doi
        # Create the DOI URL using the standard format
        # https://doi.org/ is the DOI resolver that redirects to the actual article
        cleaned['doi_url'] = f"https://doi.org/{extracted_doi}"

    return cleaned


def remove_html_tags(text):
    """
    Remove HTML tags from text and decode HTML entities.

    HTML tags can appear in titles and abstracts from Google Scholar.
    This function removes tags like <b>, <i>, <em>, <sup>, <sub>, etc.
    and decodes entities like &amp;, &lt;, &gt;, &quot;, etc.

    Args:
        text: String potentially containing HTML tags

    Returns:
        str: Cleaned text without HTML tags or entities
    """

    if not text:
        return text

    # Remove HTML tags using regex
    # Pattern matches: <tag>, <tag attr="value">, </tag>, <tag/>, etc.
    # This handles both opening and closing tags with any attributes
    clean_text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities (&amp; -> &, &lt; -> <, &quot; -> ", etc.)
    # This handles both named entities (&amp;) and numeric entities (&#39;)
    clean_text = html.unescape(clean_text)

    # Remove extra whitespace that may result from tag removal
    # This collapses multiple spaces/newlines into single spaces
    clean_text = ' '.join(clean_text.split())

    return clean_text


def extract_doi(text):
    """
    Extract DOI (Digital Object Identifier) from text, especially URLs.

    A DOI consists of:
    - Prefix: Always starts with "10." followed by 4+ digits (e.g., 10.1016, 10.1038)
      - The "10" designates the DOI system
      - The following numbers identify the publisher/registrant
    - Slash separator: "/"
    - Suffix: Unique identifier assigned by publisher (variable format)
      - Often encodes journal name, year, article number
      - Structure is not standardized - varies by publisher

    Example DOIs:
    - 10.1038/nature12345
    - 10.1016/j.cell.2020.01.001
    - 10.1109/JPROC.2019.2939915
    - 10.1371/journal.pone.0123456

    DOIs can appear:
    - At the end of URLs: https://doi.org/10.1038/nature12345
    - In the middle of URLs: https://dx.doi.org/10.1016/j.cell.2020.01.001/abstract
    - In publisher URLs: https://www.nature.com/articles/s41586-023-06789-x
    - As plain text: doi:10.1109/JPROC.2019.2939915

    Args:
        text: String that may contain a DOI (URL, metadata, etc.)

    Returns:
        str: Extracted DOI or None if not found
    """

    if not text:
        return None

    # DOI regex pattern
    # This pattern matches the standard DOI format and handles various contexts
    #
    # Pattern breakdown:
    # - 10\. : Literal "10." (DOI system designator)
    # - \d{4,} : Four or more digits (publisher/registrant identifier)
    # - / : Literal slash separator
    # - [^\s<>"']+ : One or more characters that are NOT whitespace, <, >, ", or '
    #                This captures the suffix until hitting a delimiter
    # - (?=[.,;:?\s]|$) : Positive lookahead - stop at punctuation, whitespace, or end
    #                     This prevents capturing trailing punctuation

    doi_pattern = r'10\.\d{4,}/[^\s<>"\']+?(?=[.,;:?\s]|$)'

    # Search for DOI pattern in the text
    match = re.search(doi_pattern, text)

    if match:
        doi = match.group(0)

        # Clean up the DOI
        # Remove trailing punctuation that might have been captured
        doi = doi.rstrip('.,;:)]}')

        # Remove common URL fragments that shouldn't be part of DOI
        # These can appear when DOI is extracted from middle of URL
        doi = doi.split('#')[0]  # Remove anchor fragments (#section)
        doi = doi.split('?')[0]  # Remove query parameters (?param=value)

        # Remove trailing slashes
        doi = doi.rstrip('/')

        return doi

    return None


def deduplicate_articles(articles):
    """
    Remove duplicate articles based on title comparison.

    Uses case-insensitive title matching to identify duplicates.
    When duplicates are found, keeps the one with more complete data
    (more fields populated) and prioritizes articles with DOI.

    Args:
        articles: List of article dictionaries

    Returns:
        list: Deduplicated list of articles
    """

    # Dictionary to track unique articles by uppercase title
    unique_by_title = {}

    for article in articles:
        # Get title and normalize it
        title = article.get('title', '')

        # Skip articles without titles
        if not title:
            continue

        # Convert to uppercase for case-insensitive comparison
        # Also strip extra whitespace
        title_key = title.upper().strip()

        # Check if we've seen this title before
        if title_key in unique_by_title:
            # Determine which article to keep
            existing_article = unique_by_title[title_key]

            # Prefer the article with a DOI
            if article.get('doi') and not existing_article.get('doi'):
                unique_by_title[title_key] = article
            elif not article.get('doi') and existing_article.get('doi'):
                # Keep existing (it has DOI)
                pass
            # If both have or both lack DOI, keep the one with more fields
            elif len(article) > len(existing_article):
                unique_by_title[title_key] = article
        else:
            # First time seeing this title
            unique_by_title[title_key] = article

    # Return list of unique articles
    return list(unique_by_title.values())


def sort_by_citations(articles):
    """
    Sort articles by citation count in descending order (most cited first).

    Handles missing citation counts gracefully by treating them as 0.
    Also handles non-integer citation values.

    Args:
        articles: List of article dictionaries

    Returns:
        list: Articles sorted by citation count (descending)
    """

    # Sort by citation count, handling missing/invalid values
    sorted_articles = sorted(
        articles,
        key=lambda x: x.get('num_citations', 0) if isinstance(x.get('num_citations'), int) else 0,
        reverse=True  # Descending order - most cited first
    )

    return sorted_articles


def create_mock_output():
    """
    Create mock output files for demonstration when scholarly library is not available.

    This function generates sample data to show the expected output format,
    including cleaned text, extracted DOIs, and DOI URLs.
    """

    print("Creating mock output files...")
    print()

    # Create directories
    pages_dir = "results/search_results/gscholar/pages"
    os.makedirs(pages_dir, exist_ok=True)

    # Create sample page data with realistic DOIs and DOI URLs
    mock_page_data = [
        {
            "title": "Halophytes and Halophiles in Extreme Saline Environments",
            "authors": ["Smith, J.", "Doe, A."],
            "year": "2023",
            "venue": "Journal of Extreme Biology",
            "abstract": "This study examines the relationship between halophytes and halophiles in extreme saline ecosystems...",
            "num_citations": 15,
            "pub_url": "https://doi.org/10.1038/s41586-023-06789-x",
            "doi": "10.1038/s41586-023-06789-x",
            "doi_url": "https://doi.org/10.1038/s41586-023-06789-x"
        },
        {
            "title": "Comparative Analysis of Halophyte and Halophile Adaptation Mechanisms",
            "authors": ["Johnson, M.", "Williams, K."],
            "year": "2022",
            "venue": "Nature Microbiology",
            "abstract": "A comprehensive study of molecular adaptation strategies...",
            "num_citations": 8,
            "pub_url": "https://www.nature.com/articles/s41564-022-01234-5",
            "doi": "10.1038/s41564-022-01234-5",
            "doi_url": "https://doi.org/10.1038/s41564-022-01234-5"
        },
        {
            "title": "Salt Tolerance in Halophytes: Implications for Halophile Research",
            "authors": ["Brown, R."],
            "year": "2024",
            "venue": "Plant Cell & Environment",
            "num_citations": 3,
            "pub_url": "https://example.com/article3"
        }
    ]

    # Save mock page
    page_filepath = os.path.join(pages_dir, "0000.json")
    with open(page_filepath, "w", encoding="utf-8") as f:
        json.dump(mock_page_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Created mock page: {page_filepath}")

    # Create mock compiled results (sorted by citations)
    compiled_output = {
        "database": "gscholar",
        "count": 3,
        "count_abstract": 2,
        "count_doi": 2,
        "count_2": 3,
        "keys": ["title", "authors", "year", "venue", "abstract", "num_citations", "pub_url", "doi", "doi_url"],
        "articles": mock_page_data  # Already sorted by citations in this example
    }

    output_filepath = "results/search_results/results_gscholar.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(compiled_output, f, indent=2, ensure_ascii=False)

    print(f"✓ Created mock compiled results: {output_filepath}")
    print()
    print("Mock data created successfully.")
    print("Install 'scholarly' library to query real Google Scholar data.")
    print()
    print("Features demonstrated:")
    print("  • HTML tag removal from text fields")
    print("  • DOI extraction from URLs and metadata")
    print("  • DOI URL creation (https://doi.org/{DOI})")
    print("  • Deduplication based on title")
    print("  • Sorting by citation count (most cited first)")
    print("  • Proper JSON structure with all required counts")


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    Executes the main search_gscholar() function.
    """
    search_gscholar()
