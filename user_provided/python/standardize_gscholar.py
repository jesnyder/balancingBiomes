"""
Date: January 29, 2026

Objective:
Compile and Standardize the results from Google Scholar query by reading multiple JSON
formats, cleaning data, extracting DOIs, enriching with metadata from CrossRef/OpenAlex/
Semantic Scholar, and saving in a standardized format.

Tasks:
1. Compile Google Scholar Results
   - Read all JSON files from results/search_results/gscholar/pages/
   - Handle two formats: direct list of articles OR nested under "results" key
   - Combine all articles into single list

2. Clean Article List (First Pass)
   - Remove existing "doi" and "doi_url" keys (will be regenerated)
   - Remove HTML tags from text fields
   - Remove format tags like [HTML], [PDF], [BOOK], [B]
   - Remove leading/trailing whitespace
   - Deduplicate based on title (case-insensitive)

3. Standardize Citation Field
   - Rename "num_citations" to "citations" for consistency
   - If both exist, keep "citations" and delete "num_citations"

4. Extract and Add DOI Information
   - Search for DOI pattern in pub_url field
   - DOI format: 10.XXXX/suffix
   - Add "doi" and "doi_url" fields to each article
   - Handle DOIs in middle or end of URLs
   - Remove URL fragments like .pdf, /full

5. Enrich Article Metadata with Abstracts
   - For each article, try to get abstract from:
     a) CrossRef (using DOI or title)
     b) OpenAlex (if CrossRef fails, using DOI or title)
     c) Semantic Scholar (if both fail, using DOI or title)
   - Add citations count and publisher info when available
   - 2-second delay between requests to avoid blocking
   - Progress reporting with percentage completion

6. Clean Article List (Second Pass)
   - Remove HTML tags again (from enriched data)
   - Remove format tags
   - Deduplicate again

7. Save Standardized Results
   - Save to: results/search_results/standardized/gscholar.json
   - Sort by citation count (most cited first)
   - Include counts: total, with_abstract, with_doi, with_2+_citations
   - Include list of all keys found across articles

Input:
- Directory: results/search_results/gscholar/pages/ (JSON files)
- Packages: json, os, re, html, time, glob, requests

Output:
- File: results/search_results/standardized/gscholar.json
  Structure: {count, count_2, count_abstract, count_doi, keys, results}
"""

import json
import os
import re
import html
import time
import glob
from datetime import datetime

# Try to import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: 'requests' library not available. Metadata enrichment will be skipped.")
    print("Install with: pip install requests")


def standardize_gscholar():
    """
    Main function to standardize Google Scholar search results.

    Orchestrates the complete workflow:
    1. Compile articles from multiple JSON files
    2. Clean and deduplicate
    3. Standardize citation fields
    4. Extract DOIs
    5. Enrich with metadata from external APIs
    6. Final cleaning and deduplication
    7. Save standardized results
    """

    print("=" * 80)
    print("GOOGLE SCHOLAR RESULTS STANDARDIZATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # ========================================================================
    # TASK 1: COMPILE GOOGLE SCHOLAR RESULTS
    # ========================================================================

    print("TASK 1: Compiling Google Scholar Results")
    print("-" * 80)

    pages_dir = "results/search_results/gscholar/pages"

    # Find all JSON files in the pages directory
    json_files = glob.glob(os.path.join(pages_dir, "*.json"))
    json_files.sort()  # Sort to process in order

    print(f"Found {len(json_files)} JSON files to process")
    print()

    all_articles = []

    # Process each JSON file
    for idx, filepath in enumerate(json_files, 1):
        filename = os.path.basename(filepath)
        print(f"  [{idx}/{len(json_files)}] Reading {filename}...", end=" ")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle two different JSON formats
            if isinstance(data, list):
                # Format #1: Direct list of articles
                articles_in_file = data
                print(f"✓ Got {len(articles_in_file)} articles (Format #1: direct list)")

            elif isinstance(data, dict) and 'results' in data:
                # Format #2: Articles under "results" key
                articles_in_file = data['results']
                print(f"✓ Got {len(articles_in_file)} articles (Format #2: nested under 'results')")

            else:
                # Unknown format
                print(f"⚠ Unknown format, skipping")
                continue

            # Add articles to our master list
            all_articles.extend(articles_in_file)

        except Exception as e:
            print(f"⚠ Error reading file: {str(e)}")
            continue

    print()
    print(f"✓ Total articles compiled: {len(all_articles)}")
    print()

    # ========================================================================
    # TASK 2: CLEAN ARTICLE LIST (FIRST PASS)
    # ========================================================================

    print("TASK 2: Cleaning Article List (First Pass)")
    print("-" * 80)

    print("Removing existing DOI fields (will be regenerated)...")
    for article in all_articles:
        # Remove doi and doi_url keys if they exist
        # We'll regenerate these from pub_url
        if 'doi' in article:
            del article['doi']
        if 'doi_url' in article:
            del article['doi_url']

    print("✓ Removed existing DOI fields")
    print()

    print("Cleaning text fields (HTML tags, format markers, whitespace)...")
    cleaned_count = 0
    for article in all_articles:
        # Clean all string fields in the article
        for key, value in list(article.items()):
            if isinstance(value, str):
                original = value
                cleaned = clean_text_field(value)
                if cleaned != original:
                    article[key] = cleaned
                    cleaned_count += 1

    print(f"✓ Cleaned {cleaned_count} text fields")
    print()

    print("Deduplicating articles...")
    before_dedup = len(all_articles)
    all_articles = deduplicate_articles(all_articles)
    duplicates_removed = before_dedup - len(all_articles)
    print(f"✓ Removed {duplicates_removed} duplicates")
    print(f"✓ Unique articles: {len(all_articles)}")
    print()

    # ========================================================================
    # TASK 3: STANDARDIZE CITATION FIELD
    # ========================================================================

    print("TASK 3: Standardizing Citation Field")
    print("-" * 80)

    standardized_count = 0
    for article in all_articles:
        # If num_citations exists, rename it to citations
        if 'num_citations' in article:
            if 'citations' in article:
                # Both exist - keep citations, delete num_citations
                del article['num_citations']
            else:
                # Only num_citations exists - rename it
                article['citations'] = article.pop('num_citations')
                standardized_count += 1

    print(f"✓ Standardized {standardized_count} articles")
    print()

    # ========================================================================
    # TASK 4: EXTRACT AND ADD DOI INFORMATION
    # ========================================================================

    print("TASK 4: Extracting DOI from URLs")
    print("-" * 80)

    doi_found_count = 0

    for article in all_articles:
        # Initialize DOI fields as empty
        article['doi'] = ""
        article['doi_url'] = ""

        # Try to extract DOI from pub_url or title_link
        pub_url = article.get('pub_url', '') or article.get('title_link', '')

        if pub_url:
            doi = extract_doi_from_url(pub_url)
            if doi:
                article['doi'] = doi
                article['doi_url'] = f"https://doi.org/{doi}"
                doi_found_count += 1

    print(f"✓ Extracted DOI for {doi_found_count}/{len(all_articles)} articles")
    print()

    # ========================================================================
    # TASK 5: ENRICH ARTICLE METADATA WITH ABSTRACTS
    # ========================================================================

    print("TASK 5: Enriching Article Metadata")
    print("-" * 80)

    if not REQUESTS_AVAILABLE:
        print("⚠ Skipping metadata enrichment (requests library not available)")
        print()
    else:
        print(f"Will attempt to enrich {len(all_articles)} articles")
        print("Sources: CrossRef → OpenAlex → Semantic Scholar")
        print("Delay: 2 seconds between requests")
        print()

        crossref_count = 0
        openalex_count = 0
        semantic_count = 0

        for idx, article in enumerate(all_articles, 1):
            # Progress indicator
            percent = (idx / len(all_articles)) * 100
            title_preview = article.get('title', 'No title')[:50]

            print(f"[{idx}/{len(all_articles)} - {percent:.1f}%] {title_preview}...")

            # Check if abstract already exists
            if article.get('abstract'):
                print(f"  ✓ Abstract already present, skipping enrichment")
                print()
                continue

            # Determine search identifiers
            doi = article.get('doi', '')
            title = article.get('title', '')

            # Try CrossRef first
            print(f"  Querying CrossRef...", end=" ")
            metadata = query_crossref(doi if doi else title, doi if doi else None)

            if metadata:
                crossref_count += 1
                print(f"✓ Found")

                # Add metadata from CrossRef
                if metadata.get('abstract'):
                    article['abstract'] = metadata['abstract']
                    print(f"    ✓ Abstract added from CrossRef")

                if metadata.get('is-referenced-by-count'):
                    # Only update if not already present
                    if not article.get('citations'):
                        article['citations'] = metadata['is-referenced-by-count']
                        print(f"    ✓ Citations added: {metadata['is-referenced-by-count']}")

                if metadata.get('publisher'):
                    article['publisher'] = metadata['publisher']
                    print(f"    ✓ Publisher added: {metadata['publisher'][:40]}...")

                print()
                time.sleep(2)  # Rate limiting
                continue  # Move to next article
            else:
                print(f"✗ Not found")

            # Try OpenAlex if CrossRef didn't work
            print(f"  Querying OpenAlex...", end=" ")
            time.sleep(2)  # Rate limiting

            metadata = query_openalex(doi if doi else title, doi if doi else None)

            if metadata:
                openalex_count += 1
                print(f"✓ Found")

                # Add metadata from OpenAlex
                if metadata.get('abstract_inverted_index'):
                    # Invert the inverted index to get abstract text
                    abstract = invert_abstract_index(metadata['abstract_inverted_index'])
                    article['abstract'] = abstract
                    print(f"    ✓ Abstract added from OpenAlex")

                if metadata.get('cited_by_count'):
                    if not article.get('citations'):
                        article['citations'] = metadata['cited_by_count']
                        print(f"    ✓ Citations added: {metadata['cited_by_count']}")

                if metadata.get('host_organization_name'):
                    article['publisher'] = metadata['host_organization_name']
                    print(f"    ✓ Publisher added: {metadata['host_organization_name'][:40]}...")

                print()
                time.sleep(2)  # Rate limiting
                continue  # Move to next article
            else:
                print(f"✗ Not found")

            # Try Semantic Scholar if both CrossRef and OpenAlex failed
            print(f"  Querying Semantic Scholar...", end=" ")
            time.sleep(2)  # Rate limiting

            metadata = query_semantic_scholar(doi if doi else title, doi if doi else None)

            if metadata:
                semantic_count += 1
                print(f"✓ Found")

                # Add metadata from Semantic Scholar
                if metadata.get('abstract'):
                    article['abstract'] = metadata['abstract']
                    print(f"    ✓ Abstract added from Semantic Scholar")

                if metadata.get('citationCount'):
                    if not article.get('citations'):
                        article['citations'] = metadata['citationCount']
                        print(f"    ✓ Citations added: {metadata['citationCount']}")

                print()
            else:
                print(f"✗ Not found")
                print(f"  ⚠ No abstract found in any source")

            print()

        print()
        print(f"📊 Enrichment Summary:")
        print(f"  CrossRef: {crossref_count} articles")
        print(f"  OpenAlex: {openalex_count} articles")
        print(f"  Semantic Scholar: {semantic_count} articles")
        print(f"  Total enriched: {crossref_count + openalex_count + semantic_count}")
        print()

    # ========================================================================
    # TASK 6: CLEAN ARTICLE LIST (SECOND PASS)
    # ========================================================================

    print("TASK 6: Cleaning Article List (Second Pass)")
    print("-" * 80)

    print("Cleaning text fields again (from enriched data)...")
    cleaned_count = 0
    for article in all_articles:
        for key, value in list(article.items()):
            if isinstance(value, str):
                original = value
                cleaned = clean_text_field(value)
                if cleaned != original:
                    article[key] = cleaned
                    cleaned_count += 1

    print(f"✓ Cleaned {cleaned_count} text fields")
    print()

    print("Deduplicating articles again...")
    before_dedup = len(all_articles)
    all_articles = deduplicate_articles(all_articles)
    duplicates_removed = before_dedup - len(all_articles)
    print(f"✓ Removed {duplicates_removed} duplicates")
    print(f"✓ Unique articles: {len(all_articles)}")
    print()

    # ========================================================================
    # TASK 7: SAVE STANDARDIZED RESULTS
    # ========================================================================

    print("TASK 7: Saving Standardized Results")
    print("-" * 80)

    # Sort articles by citation count (most cited first)
    all_articles.sort(
        key=lambda x: x.get('citations', 0) if isinstance(x.get('citations'), int) else 0,
        reverse=True
    )
    print(f"✓ Sorted {len(all_articles)} articles by citation count")

    # Count statistics
    count_total = len(all_articles)

    count_abstract = sum(1 for a in all_articles if a.get('abstract'))

    count_doi = sum(1 for a in all_articles if a.get('doi'))

    count_2_citations = sum(
        1 for a in all_articles
        if isinstance(a.get('citations'), int) and a.get('citations', 0) >= 2
    )

    # Collect all unique keys
    all_keys = set()
    for article in all_articles:
        all_keys.update(article.keys())
    all_keys = sorted(list(all_keys))

    print()
    print(f"📊 Statistics:")
    print(f"  Total articles: {count_total}")
    print(f"  With abstract: {count_abstract}")
    print(f"  With DOI: {count_doi}")
    print(f"  With 2+ citations: {count_2_citations}")
    print(f"  Unique fields: {len(all_keys)}")
    print()

    # Build output structure
    standardized_output = {
        "count": count_total,
        "count_2": count_2_citations,
        "count_abstract": count_abstract,
        "count_doi": count_doi,
        "keys": all_keys,
        "results": all_articles
    }

    # Ensure output directory exists
    output_dir = "results/search_results/standardized"
    os.makedirs(output_dir, exist_ok=True)

    # Save to file
    output_filepath = os.path.join(output_dir, "gscholar.json")
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(standardized_output, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_filepath)
    print(f"✓ Saved to: {output_filepath}")
    print(f"  File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    print()

    # ========================================================================
    # COMPLETION
    # ========================================================================

    print("=" * 80)
    print("✓ STANDARDIZATION COMPLETE")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"📄 Output: {output_filepath}")
    print()
    print("=" * 80)


def clean_text_field(text):
    """
    Clean text field by removing HTML tags, format markers, and extra whitespace.

    Removes:
    - HTML tags like <b>, <i>, <em>, etc.
    - Format markers like [HTML], [PDF], [BOOK], [B]
    - Leading and trailing whitespace
    - HTML entities (&amp;, &lt;, etc.)

    Args:
        text: String to clean

    Returns:
        Cleaned string
    """

    if not text or not isinstance(text, str):
        return text

    # Remove HTML tags (anything between < and >)
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities (&amp; -> &, &lt; -> <, etc.)
    text = html.unescape(text)

    # Remove format markers like [HTML], [PDF], [BOOK], [B]
    # Pattern matches [WORD] where WORD is all caps
    text = re.sub(r'\[(?:HTML|PDF|BOOK|B|XML|DOC|CITATION)\]', '', text, flags=re.IGNORECASE)

    # Remove extra whitespace (multiple spaces, newlines, tabs)
    text = ' '.join(text.split())

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


def deduplicate_articles(articles):
    """
    Remove duplicate articles based on title comparison.

    Uses case-insensitive title matching. When duplicates found,
    keeps the one with more complete data (more fields).

    Args:
        articles: List of article dictionaries

    Returns:
        List of unique articles
    """

    unique_articles = {}

    for article in articles:
        # Get title and normalize it
        title = article.get('title', '')

        # Skip articles without titles
        if not title:
            continue

        # Create case-insensitive key
        title_key = title.upper().strip()

        # Check for duplicate
        if title_key in unique_articles:
            # Keep the one with more fields
            existing = unique_articles[title_key]
            if len(article) > len(existing):
                unique_articles[title_key] = article
        else:
            unique_articles[title_key] = article

    return list(unique_articles.values())


def extract_doi_from_url(url):
    """
    Extract DOI from a URL.

    DOI format: 10.XXXX/suffix
    - Prefix: 10. followed by 4-9 digits
    - Suffix: variable format (letters, numbers, periods, dashes)

    Handles:
    - DOI at end of URL
    - DOI in middle of URL
    - Removes .pdf, /full suffixes

    Examples:
    - https://onlinelibrary.wiley.com/doi/abs/10.1002/9780470015902.a0000394.pub3
      → 10.1002/9780470015902.a0000394.pub3
    - https://link.springer.com/content/pdf/10.1007/1-4020-4018-0.pdf
      → 10.1007/1-4020-4018-0
    - https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2018.00148/full
      → 10.3389/fmicb.2018.00148

    Args:
        url: URL string that may contain a DOI

    Returns:
        Extracted DOI string or empty string if not found
    """

    if not url:
        return ""

    # DOI regex pattern
    # Matches: 10.XXXX/suffix
    # Suffix can contain: letters, numbers, dots, dashes, slashes (but not .pdf or /full)
    doi_pattern = r'10\.\d{4,9}/[^\s"<>]+?(?=\.pdf|/full|\.html|/abstract|/pdf|\s|$|&|#|\?)'

    # Also try a more permissive pattern
    doi_pattern_permissive = r'10\.\d{4,9}/[^\s"<>]+'

    # Try strict pattern first
    match = re.search(doi_pattern, url)
    if match:
        doi = match.group(0)
    else:
        # Try permissive pattern
        match = re.search(doi_pattern_permissive, url)
        if match:
            doi = match.group(0)
        else:
            return ""

    # Clean up the DOI
    # Remove trailing punctuation
    doi = doi.rstrip('.,;:)]}')

    # Remove .pdf suffix
    if doi.endswith('.pdf'):
        doi = doi[:-4]

    # Remove /full suffix
    if doi.endswith('/full'):
        doi = doi[:-5]

    # Remove /abstract suffix
    if doi.endswith('/abstract'):
        doi = doi[:-9]

    # Remove /pdf suffix
    if doi.endswith('/pdf'):
        doi = doi[:-4]

    # Remove .html suffix
    if doi.endswith('.html'):
        doi = doi[:-5]

    # Remove trailing slash
    doi = doi.rstrip('/')

    return doi


def query_crossref(identifier, is_doi=None):
    """
    Query CrossRef API for article metadata.

    Args:
        identifier: DOI or title to search for
        is_doi: True if identifier is DOI, False/None if title

    Returns:
        Dictionary with metadata or None if not found
    """

    try:
        if is_doi:
            # Query by DOI
            url = f"https://api.crossref.org/works/{identifier}"
        else:
            # Query by title
            url = f"https://api.crossref.org/works"
            params = {'query.title': identifier, 'rows': 1}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()
            items = data.get('message', {}).get('items', [])

            if not items:
                return None

            # Return first match
            return items[0]

        # For DOI query
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        return data.get('message', {})

    except Exception as e:
        return None


def query_openalex(identifier, is_doi=None):
    """
    Query OpenAlex API for article metadata.

    Args:
        identifier: DOI or title to search for
        is_doi: True if identifier is DOI, False/None if title

    Returns:
        Dictionary with metadata or None if not found
    """

    try:
        if is_doi:
            # Query by DOI
            url = f"https://api.openalex.org/works/doi:{identifier}"
        else:
            # Query by title
            url = "https://api.openalex.org/works"
            params = {'filter': f'title.search:{identifier}', 'per-page': 1}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()
            results = data.get('results', [])

            if not results:
                return None

            # Return first match
            return results[0]

        # For DOI query
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:
        return None


def query_semantic_scholar(identifier, is_doi=None):
    """
    Query Semantic Scholar API for article metadata.

    Args:
        identifier: DOI or title to search for
        is_doi: True if identifier is DOI, False/None if title

    Returns:
        Dictionary with metadata or None if not found
    """

    try:
        if is_doi:
            # Query by DOI
            url = f"https://api.semanticscholar.org/v1/paper/{identifier}"
        else:
            # Semantic Scholar doesn't have good title search in v1
            # Skip title-based search
            return None

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:
        return None


def invert_abstract_index(inverted_index):
    """
    Convert OpenAlex inverted abstract index back to text.

    OpenAlex stores abstracts as inverted indices:
    {"word1": [0, 5], "word2": [1, 3]} means:
    - "word1" appears at positions 0 and 5
    - "word2" appears at positions 1 and 3

    Args:
        inverted_index: Dictionary mapping words to position lists

    Returns:
        Abstract text as string
    """

    if not inverted_index:
        return ""

    # Create a list to hold words at each position
    max_position = 0
    for positions in inverted_index.values():
        if positions:
            max_position = max(max_position, max(positions))

    # Initialize word array
    words = [''] * (max_position + 1)

    # Place each word at its positions
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word

    # Join words into text
    abstract = ' '.join(words)

    return abstract


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    Executes the main standardize_gscholar() function.
    """
    standardize_gscholar()
