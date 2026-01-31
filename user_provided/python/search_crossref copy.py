"""
Date prepared: January 29, 2026

Objective of the code:
Query the CrossRef API to retrieve scientific articles containing both "Halophyte" AND "Halophile",
process and clean the results with case-insensitive journal title matching, generate structured
JSON output files, and create TWO interactive JavaScript tables using Tabulator library:
1. Table of journal titles with article counts
2. Table of articles (with 2+ citations only) with full metadata

Tasks:
1. Query CrossRef API (https://www.crossref.org/)
   - Use the CrossRef REST API endpoint: https://api.crossref.org/works
   - Search query: "Halophyte AND Halophile" (articles citing both terms)
   - Implement pagination to retrieve up to 20,000 results
   - Retrieve 100 results per API call (rows parameter)
   - Wait 3 seconds between consecutive API requests to respect rate limits
   - Store all results in a single dictionary variable
   - Package required: requests (for HTTP API calls)
   - Package required: time (for delays between requests)

2. Clean the retrieved results
   - Remove duplicate entries based on DOI (Digital Object Identifier)
   - Sort articles by citation count in descending order (most cited first)
   - Citation count field: "is-referenced-by-count" in CrossRef data

3. Save article results as JSON
   - Create "results" directory if it doesn't exist
   - Save to: "results/results_crossref.json"
   - JSON structure includes: database name, various counts, field keys, and articles array
   - Package required: json (for JSON serialization)
   - Package required: os (for directory operations)

4. Extract and analyze journal titles (CASE-INSENSITIVE)
   - Extract unique journal titles from "container-title" field
   - Compare titles using uppercase conversion (case-insensitive matching)
   - Count articles per journal (grouping case variations together)
   - Store original capitalization for display
   - Sort journals by article count (descending)
   - Save to: "results/titles.json"
   - Package required: collections.defaultdict (for counting)

5. Generate interactive JavaScript table for TITLES using Tabulator
   - Create JavaScript code using Tabulator library (https://tabulator.info/)
   - Build sortable, filterable table with column headers
   - Embed JSON data directly in JavaScript file
   - Features: column sorting, header filters, pagination (20 per page)
   - Include journal website and impact factor lookups
   - Save to: "docs/js/table_titles.js"
   - Include HTML integration instructions in file header

6. Generate interactive JavaScript table for ARTICLES using Tabulator
   - Create JavaScript code using Tabulator library (https://tabulator.info/)
   - Display only articles with 2+ citations
   - Build sortable, filterable table with article metadata
   - Features: column sorting, header filters, pagination (20 per page)
   - Columns: title (with DOI link), type, where published, year, citation count
   - Save to: "docs/js/table_articles.js"
   - Include HTML integration instructions in file header

Input:
- CrossRef REST API: https://api.crossref.org/works
- Query parameters: query="Halophyte AND Halophile", rows=100, offset=variable

Output:
- results/results_crossref.json: Complete article dataset with metadata
- results/titles.json: Journal titles with article counts (case-insensitive grouped)
- docs/js/table_titles.js: Interactive Tabulator table for journal titles
- docs/js/table_articles.js: Interactive Tabulator table for articles (2+ citations)
"""

import requests
import json
import time
import os
from collections import defaultdict
from datetime import datetime


def search_crossref():
    """
    Main function to execute the complete CrossRef search workflow.

    This function orchestrates all tasks:
    1. Query CrossRef API with pagination
    2. Clean and sort results
    3. Save article data
    4. Extract journal titles (case-insensitive)
    5. Generate interactive Tabulator JavaScript table for titles
    6. Generate interactive Tabulator JavaScript table for articles

    Returns:
        None (outputs are saved to files)
    """

    # ========================================================================
    # STEP 1: QUERY CROSSREF API
    # ========================================================================

    print("=" * 80)
    print("CROSSREF ARTICLE SEARCH AND ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Search Query: (Halophyte AND Halophile)")
    print("=" * 80)
    print()

    # CrossRef API configuration
    # The base URL for the CrossRef REST API works endpoint
    base_url = "https://api.crossref.org/works"

    # Search parameters
    # We're looking for articles that mention both "Halophyte" AND "Halophile"
    search_query = "Halophyte AND Halophile"

    # Pagination settings
    results_per_page = 100  # Number of results to fetch per API call
    max_total_results = 20000  # Maximum total results to retrieve
    wait_time = 3  # Seconds to wait between API calls

    # Storage for all articles
    # We use a dictionary with DOI as the key to automatically prevent duplicates
    all_articles_dict = {}

    # Pagination tracking variables
    current_offset = 0  # Starting position for pagination
    total_fetched = 0  # Total number of results fetched so far
    page_number = 1  # Current page number (for display purposes)

    print("Starting API queries...")
    print(f"Configuration: {results_per_page} results per page, up to {max_total_results} total")
    print("-" * 80)
    print()

    # Continue fetching until we reach the maximum or run out of results
    while total_fetched < max_total_results:

        # Prepare API request parameters
        # The CrossRef API uses 'query' for search terms, 'rows' for page size,
        # and 'offset' for pagination starting position
        params = {
            "query": search_query,
            "rows": results_per_page,
            "offset": current_offset
        }

        print(f"Page {page_number}: Fetching results {current_offset + 1} to {current_offset + results_per_page}...")

        try:
            # Make HTTP GET request to CrossRef API
            # The requests library automatically handles URL encoding of parameters
            response = requests.get(base_url, params=params)

            # Check if the request was successful (HTTP status code 200)
            if response.status_code != 200:
                print(f"  ⚠ ERROR: API returned status code {response.status_code}")
                print(f"  Response text: {response.text}")
                print(f"  Stopping pagination and continuing with data collected so far.")
                break

            # Parse the JSON response
            data = response.json()

            # Extract the list of articles from the response
            # CrossRef API structure: response > message > items (array of articles)
            articles_in_response = data.get("message", {}).get("items", [])

            # If we get no results, we've reached the end of available data
            if not articles_in_response:
                print(f"  ℹ No more results available. Ending pagination.")
                break

            # Process each article in this page of results
            new_articles_count = 0
            for article in articles_in_response:
                # Every CrossRef article has a unique DOI (Digital Object Identifier)
                doi = article.get("DOI")

                if doi:
                    # Only add if this DOI hasn't been seen before
                    # This prevents duplicates automatically
                    if doi not in all_articles_dict:
                        all_articles_dict[doi] = article
                        new_articles_count += 1

            # Display progress information
            print(f"  ✓ Retrieved: {len(articles_in_response)} results")
            print(f"  ✓ New unique articles: {new_articles_count}")
            print(f"  ✓ Total unique articles collected: {len(all_articles_dict)}")

            # Update pagination counters
            total_fetched += len(articles_in_response)
            current_offset += results_per_page
            page_number += 1

            # Check if we received fewer results than requested
            # This indicates we've reached the end of available results
            if len(articles_in_response) < results_per_page:
                print(f"  ℹ Received fewer results than requested. All available data retrieved.")
                break

            # Wait before making the next request (unless this was the last one)
            # This is polite API usage and helps avoid rate limiting
            if total_fetched < max_total_results:
                print(f"  ⏳ Waiting {wait_time} seconds before next request...")
                time.sleep(wait_time)

        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            print(f"  ⚠ ERROR: Network error occurred: {str(e)}")
            print(f"  Continuing with data collected so far ({len(all_articles_dict)} articles).")
            break

        except Exception as e:
            # Handle any other unexpected errors
            print(f"  ⚠ ERROR: Unexpected error: {str(e)}")
            print(f"  Continuing with data collected so far ({len(all_articles_dict)} articles).")
            break

    print()
    print("=" * 80)
    print(f"✓ API Query Complete: {len(all_articles_dict)} unique articles retrieved")
    print("=" * 80)
    print()

    # ========================================================================
    # STEP 2: CLEAN AND SORT RESULTS
    # ========================================================================

    print("Cleaning and sorting results...")
    print("-" * 80)

    # Convert dictionary to list for sorting
    # We've already removed duplicates by using DOI as dictionary key
    articles_list = list(all_articles_dict.values())

    print(f"✓ Total unique articles (duplicates removed via DOI): {len(articles_list)}")

    # Sort articles by citation count
    # CrossRef stores citation count in the field "is-referenced-by-count"
    # We use get() with default value 0 for articles without citation data
    # reverse=True sorts in descending order (most cited first)
    articles_list.sort(
        key=lambda article: article.get("is-referenced-by-count", 0),
        reverse=True
    )

    print(f"✓ Articles sorted by citation count (descending)")

    # Display information about the most cited article
    if articles_list:
        top_article = articles_list[0]
        top_citations = top_article.get("is-referenced-by-count", 0)
        top_title = top_article.get("title", ["Unknown"])[0] if top_article.get("title") else "Unknown"
        print(f"  Most cited article: {top_citations} citations")
        print(f"  Title: {top_title[:80]}...")

    print()

    # ========================================================================
    # STEP 3: ANALYZE RESULTS AND PREPARE METADATA
    # ========================================================================

    print("Analyzing article metadata...")
    print("-" * 80)

    # Count articles with abstracts
    # The "abstract" field may not be present in all articles
    count_with_abstract = sum(1 for article in articles_list if article.get("abstract"))
    print(f"✓ Articles with abstracts: {count_with_abstract}")

    # Count articles with at least 2 citations
    count_with_2plus_citations = sum(
        1 for article in articles_list
        if article.get("is-referenced-by-count", 0) >= 2
    )
    print(f"✓ Articles with 2+ citations: {count_with_2plus_citations}")

    # Collect all unique field keys across all articles
    # Different articles may have different fields available
    # This gives us a complete picture of what data is available
    all_field_keys = set()
    for article in articles_list:
        all_field_keys.update(article.keys())

    # Convert to sorted list for consistent output
    all_field_keys = sorted(list(all_field_keys))

    print(f"✓ Unique fields found across all articles: {len(all_field_keys)}")
    print(f"  Sample fields: {', '.join(list(all_field_keys)[:5])}...")
    print()

    # ========================================================================
    # STEP 4: SAVE ARTICLE RESULTS AS JSON
    # ========================================================================

    print("Saving article results to JSON...")
    print("-" * 80)

    # Create results directory if it doesn't exist
    # exist_ok=True prevents error if directory already exists
    os.makedirs("results", exist_ok=True)
    print(f"✓ Ensured 'results' directory exists")

    # Build the output data structure as specified
    article_output = {
        "database": "crossref",
        "count": len(articles_list),
        "count_abstract": count_with_abstract,
        "count_2": count_with_2plus_citations,
        "keys": all_field_keys,
        "articles": articles_list
    }

    # Save to JSON file
    # indent=2 makes the file human-readable with proper formatting
    # ensure_ascii=False allows Unicode characters (important for international journals)
    output_filepath = "results/results_crossref.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(article_output, f, indent=2, ensure_ascii=False)

    # Get file size for information
    file_size = os.path.getsize(output_filepath)
    print(f"✓ Article data saved to: {output_filepath}")
    print(f"  File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print()

    # ========================================================================
    # STEP 5: EXTRACT AND COUNT JOURNAL TITLES (CASE-INSENSITIVE)
    # ========================================================================

    print("Extracting journal titles (case-insensitive processing)...")
    print("-" * 80)

    # Dictionary to count occurrences of each journal title
    # We use uppercase keys for case-insensitive comparison
    # But store the original title for display purposes
    # Structure: {uppercase_title: {"original": original_title, "count": count}}
    title_data = {}

    # Iterate through all articles to extract journal titles
    for article in articles_list:
        # The "container-title" field contains the journal name
        # It's stored as a list, so we take the first element
        container_titles = article.get("container-title", [])

        if container_titles and len(container_titles) > 0:
            # Get the first (primary) journal title
            original_title = container_titles[0]

            # Convert to uppercase for case-insensitive comparison
            # This ensures "Nature", "NATURE", and "nature" are treated as the same journal
            uppercase_title = original_title.upper()

            if uppercase_title in title_data:
                # Increment count for this journal
                title_data[uppercase_title]["count"] += 1
            else:
                # First occurrence - store original title and initialize count
                title_data[uppercase_title] = {
                    "original": original_title,
                    "count": 1
                }

    print(f"✓ Found {len(title_data)} unique journal titles (case-insensitive)")
    print(f"✓ Total articles with journal information: {sum(item['count'] for item in title_data.values())}")

    # Convert to list of dictionaries for JSON output
    # Use the original title for display, not the uppercase version
    titles_list = [
        {"title": data["original"], "count": data["count"]}
        for uppercase_title, data in title_data.items()
    ]

    # Sort by count in descending order (most common journals first)
    titles_list.sort(key=lambda x: x["count"], reverse=True)

    # Display top 5 journals
    print(f"\nTop 5 journals by article count:")
    for i, item in enumerate(titles_list[:5], start=1):
        print(f"  {i}. {item['title']}: {item['count']} articles")

    # Build the output structure for journal titles
    titles_output = {
        "count": len(titles_list),
        "count_articles": sum(item["count"] for item in titles_list),
        "titles": titles_list
    }

    # Save journal titles to JSON file
    titles_filepath = "results/titles.json"
    with open(titles_filepath, "w", encoding="utf-8") as f:
        json.dump(titles_output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Journal titles saved to: {titles_filepath}")
    print()

    # ========================================================================
    # STEP 6: GENERATE INTERACTIVE TABULATOR TABLE FOR TITLES
    # ========================================================================

    print("Generating interactive Tabulator JavaScript table for TITLES...")
    print("-" * 80)

    # Ensure docs/js directory exists
    os.makedirs("docs/js", exist_ok=True)
    print(f"✓ Ensured 'docs/js' directory exists")

    # Create the JavaScript code for TITLES table using Tabulator library
    titles_js_code = f'''/*
 * Interactive Journal Titles Table using Tabulator
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 *
 * This file creates an interactive, sortable, and filterable table displaying
 * journal titles from a CrossRef search for articles about Halophytes and Halophiles.
 *
 * Library: Tabulator v6.3 (https://tabulator.info/)
 *
 * FEATURES:
 * - Sortable columns (click any column header to sort)
 * - Header filters for each column (type to filter results)
 * - Pagination (20 results per page)
 * - Displays: Journal Title, Article Count, Website, Impact Factor
 *
 * ============================================================================
 * HTML INTEGRATION INSTRUCTIONS
 * ============================================================================
 *
 * Add the following to your docs/index.html file:
 *
 * 1. In the <head> section, add Tabulator CSS and dependencies:
 *
 *    <!-- Tabulator CSS -->
 *    <link href="https://unpkg.com/tabulator-tables@6.3.0/dist/css/tabulator.min.css" rel="stylesheet">
 *
 *    <!-- Optional: Tabulator theme for better styling -->
 *    <link href="https://unpkg.com/tabulator-tables@6.3.0/dist/css/tabulator_midnight.min.css" rel="stylesheet">
 *
 *    <!-- Custom styling (optional) -->
 *    <style>
 *      .table-container {{
 *        margin: 20px;
 *        max-width: 1400px;
 *      }}
 *
 *      .table-header {{
 *        font-family: Arial, sans-serif;
 *        margin-bottom: 15px;
 *      }}
 *
 *      .table-header h2 {{
 *        color: #2c3e50;
 *        margin-bottom: 5px;
 *      }}
 *
 *      .table-header p {{
 *        color: #7f8c8d;
 *        font-size: 14px;
 *      }}
 *    </style>
 *
 * 2. In the <body> section where you want the titles table to appear:
 *
 *    <div class="table-container">
 *      <div class="table-header">
 *        <h2>Journal Titles from CrossRef Search</h2>
 *        <p>Interactive table showing journals publishing Halophyte and Halophile research</p>
 *      </div>
 *      <div id="tableOfTitles"></div>
 *    </div>
 *
 * 3. Before the closing </body> tag, include Tabulator library and this script:
 *
 *    <!-- Tabulator JavaScript library -->
 *    <script type="text/javascript" src="https://unpkg.com/tabulator-tables@6.3.0/dist/js/tabulator.min.js"></script>
 *
 *    <!-- This file (titles table configuration and data) -->
 *    <script src="js/table_titles.js"></script>
 *
 * ============================================================================
 */

// ============================================================================
// DATA SECTION
// ============================================================================

/**
 * Journal titles dataset
 * This constant contains all the journal title data embedded directly in the file.
 * Data is loaded from the CrossRef API and processed for case-insensitive matching.
 *
 * Structure:
 * {{
 *   count: Number of unique journal titles (case-insensitive)
 *   count_articles: Total number of articles across all journals
 *   titles: Array of {{title: string, count: number}} objects
 * }}
 */
const titles = {json.dumps(titles_output, indent=2, ensure_ascii=False)};

// ============================================================================
// JOURNAL INFORMATION LOOKUP FUNCTIONS
// ============================================================================

/**
 * Lookup journal website based on title
 *
 * This function attempts to determine the website URL for a journal based on
 * its title. It uses pattern matching against known publisher names and journal
 * patterns. This is a simplified approach; a production system would ideally
 * use a comprehensive database or API.
 *
 * The matching is case-insensitive to handle various capitalizations.
 *
 * @param {{string}} title - The journal title
 * @returns {{string}} - The website URL or 'N/A' if not found
 */
function getJournalWebsite(title) {{
  const lowerTitle = title.toLowerCase();

  // Check for common publishers and journal families
  if (lowerTitle.includes('plos')) return 'https://plos.org';
  if (lowerTitle.includes('nature')) return 'https://www.nature.com';
  if (lowerTitle.includes('science')) return 'https://www.science.org';
  if (lowerTitle.includes('proceedings of the national academy')) return 'https://www.pnas.org';
  if (lowerTitle.includes('frontiers in')) return 'https://www.frontiersin.org';
  if (lowerTitle.includes('bmc ')) return 'https://www.biomedcentral.com';
  if (lowerTitle.includes('springer')) return 'https://www.springer.com';
  if (lowerTitle.includes('wiley')) return 'https://www.wiley.com';
  if (lowerTitle.includes('elsevier')) return 'https://www.elsevier.com';
  if (lowerTitle.includes('taylor & francis') || lowerTitle.includes('taylor and francis')) return 'https://www.tandfonline.com';
  if (lowerTitle.includes('mdpi')) return 'https://www.mdpi.com';
  if (lowerTitle.includes('ieee')) return 'https://www.ieee.org';
  if (lowerTitle.includes('american chemical society') || lowerTitle.includes('acs ')) return 'https://www.acs.org';
  if (lowerTitle.includes('royal society')) return 'https://royalsociety.org';
  if (lowerTitle.includes('oxford')) return 'https://academic.oup.com';
  if (lowerTitle.includes('cambridge')) return 'https://www.cambridge.org';

  return 'N/A';
}}

/**
 * Lookup journal impact factor based on title
 *
 * Returns the impact factor for known journals. Impact factors are prestigious
 * metrics that measure the average number of citations to articles published
 * in a journal. These values change annually.
 *
 * Note: This is a limited lookup table with approximate values. In a production
 * environment, you would integrate with Journal Citation Reports (JCR) or a
 * similar authoritative database.
 *
 * @param {{string}} title - The journal title
 * @returns {{string}} - The impact factor as a string or 'N/A' if unknown
 */
function getImpactFactor(title) {{
  const lowerTitle = title.toLowerCase();

  // High-impact journals (approximate 2024 values)
  if (lowerTitle === 'nature') return '42.8';
  if (lowerTitle === 'science') return '41.8';
  if (lowerTitle.includes('nature communications')) return '14.7';
  if (lowerTitle.includes('proceedings of the national academy')) return '9.4';
  if (lowerTitle.includes('plos one')) return '2.9';
  if (lowerTitle.includes('plos biology')) return '7.8';
  if (lowerTitle.includes('scientific reports')) return '3.8';
  if (lowerTitle.includes('frontiers in')) return '~4.0';

  return 'N/A';
}}

// ============================================================================
// TABULATOR TABLE CONFIGURATION FOR TITLES
// ============================================================================

/**
 * Tabulator table instance for journal titles
 * This variable will hold the Tabulator table object once initialized.
 * Named as specified: tableTitles
 */
let tableTitles;

/**
 * Initialize the Tabulator table for journal titles
 *
 * This function creates and configures the Tabulator table with all necessary
 * options including columns, sorting, filtering, and pagination.
 *
 * Tabulator documentation: https://tabulator.info/docs/6.3
 */
function initializeTitlesTable() {{

  // Prepare the data with computed fields (website and impact factor)
  const tableData = titles.titles.map(item => ({{
    title: item.title,
    count: item.count,
    website: getJournalWebsite(item.title),
    impact: getImpactFactor(item.title)
  }}));

  // Create the Tabulator table
  // The table is attached to the div with id "tableOfTitles"
  tableTitles = new Tabulator("#tableOfTitles", {{

    // DATA CONFIGURATION
    data: tableData,

    // LAYOUT CONFIGURATION
    layout: "fitColumns",
    responsiveLayout: "hide",

    // PAGINATION CONFIGURATION
    // Display 20 rows per page as specified
    pagination: true,
    paginationSize: 20,
    paginationSizeSelector: [10, 20, 50, 100],

    // INITIAL SORT
    // Sort by count (descending) so most common journals appear first
    initialSort: [
      {{column: "count", dir: "desc"}}
    ],

    // COLUMN DEFINITIONS
    columns: [
      {{
        title: "Journal Title",
        field: "title",
        sorter: "string",
        headerFilter: "input",
        headerFilterPlaceholder: "Search title...",
        widthGrow: 3,
        tooltip: true
      }},

      {{
        title: "Article Count",
        field: "count",
        sorter: "number",
        headerFilter: "input",
        headerFilterPlaceholder: "Filter count...",
        width: 150,
        hozAlign: "center",
        headerHozAlign: "center"
      }},

      {{
        title: "Website",
        field: "website",
        sorter: "string",
        headerFilter: "input",
        headerFilterPlaceholder: "Filter website...",
        widthGrow: 2,
        formatter: function(cell) {{
          const url = cell.getValue();
          if (url && url !== 'N/A') {{
            return `<a href="${{url}}" target="_blank" rel="noopener noreferrer">${{url}}</a>`;
          }}
          return url;
        }},
        tooltip: true
      }},

      {{
        title: "Impact Factor",
        field: "impact",
        sorter: function(a, b) {{
          const aVal = a === 'N/A' ? -1 : parseFloat(a.replace('~', ''));
          const bVal = b === 'N/A' ? -1 : parseFloat(b.replace('~', ''));
          return aVal - bVal;
        }},
        headerFilter: "input",
        headerFilterPlaceholder: "Filter IF...",
        width: 150,
        hozAlign: "center",
        headerHozAlign: "center"
      }}
    ]
  }});

  console.log("Titles table initialized with", tableData.length, "journals");
}}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the table when the DOM is fully loaded
 */
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', initializeTitlesTable);
}} else {{
  initializeTitlesTable();
}}
'''

    # Save the JavaScript file for TITLES
    titles_js_filepath = "docs/js/table_titles.js"
    with open(titles_js_filepath, "w", encoding="utf-8") as f:
        f.write(titles_js_code)

    print(f"✓ Titles table JavaScript generated: {titles_js_filepath}")
    print(f"  Table contains {len(titles_list)} journal titles")
    print()

    # ========================================================================
    # STEP 7: GENERATE INTERACTIVE TABULATOR TABLE FOR ARTICLES
    # ========================================================================

    print("Generating interactive Tabulator JavaScript table for ARTICLES...")
    print("-" * 80)

    # Filter articles to include only those with 2+ citations
    articles_filtered = [
        article for article in articles_list
        if article.get("is-referenced-by-count", 0) >= 2
    ]

    print(f"✓ Filtering articles with 2+ citations: {len(articles_filtered)} of {len(articles_list)}")

    # Create the JavaScript code for ARTICLES table using Tabulator library
    articles_js_code = f'''/*
 * Interactive Articles Table using Tabulator
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 *
 * This file creates an interactive, sortable, and filterable table displaying
 * articles from a CrossRef search for articles about Halophytes and Halophiles.
 *
 * ONLY ARTICLES WITH 2+ CITATIONS ARE DISPLAYED
 *
 * Library: Tabulator v6.3 (https://tabulator.info/)
 *
 * FEATURES:
 * - Sortable columns (click any column header to sort)
 * - Header filters for each column (type to filter results)
 * - Pagination (20 results per page)
 * - Clickable article titles with DOI links
 * - Displays: Title, Type, Where Published, Year, Citation Count
 *
 * ============================================================================
 * HTML INTEGRATION INSTRUCTIONS
 * ============================================================================
 *
 * Add the following to your docs/index.html file:
 *
 * 1. In the <head> section, add Tabulator CSS (if not already added):
 *
 *    <!-- Tabulator CSS -->
 *    <link href="https://unpkg.com/tabulator-tables@6.3.0/dist/css/tabulator.min.css" rel="stylesheet">
 *
 *    <!-- Optional: Tabulator theme -->
 *    <link href="https://unpkg.com/tabulator-tables@6.3.0/dist/css/tabulator_midnight.min.css" rel="stylesheet">
 *
 * 2. In the <body> section where you want the articles table to appear:
 *
 *    <div class="table-container">
 *      <div class="table-header">
 *        <h2>Articles from CrossRef Search</h2>
 *        <p>Articles with 2+ citations about Halophyte and Halophile research</p>
 *      </div>
 *      <div id="tableOfArticles"></div>
 *    </div>
 *
 * 3. Before the closing </body> tag, include Tabulator library and this script:
 *
 *    <!-- Tabulator JavaScript library (if not already included) -->
 *    <script type="text/javascript" src="https://unpkg.com/tabulator-tables@6.3.0/dist/js/tabulator.min.js"></script>
 *
 *    <!-- This file (articles table configuration and data) -->
 *    <script src="js/table_articles.js"></script>
 *
 * ============================================================================
 */

// ============================================================================
// DATA SECTION
// ============================================================================

/**
 * Articles dataset (filtered to 2+ citations only)
 * This constant contains all article data embedded directly in the file.
 *
 * Note: Variable name is "articles" as specified (not "aticles")
 * Only articles with at least 2 citations are included
 */
const articles = {json.dumps(articles_filtered, indent=2, ensure_ascii=False)};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Extract article title from CrossRef data
 *
 * CrossRef stores titles as an array. This function extracts the first
 * (primary) title and handles cases where title might be missing.
 *
 * @param {{object}} article - The article object from CrossRef
 * @returns {{string}} - The article title or "Untitled"
 */
function getArticleTitle(article) {{
  if (article.title && article.title.length > 0) {{
    return article.title[0];
  }}
  return "Untitled";
}}

/**
 * Get the DOI URL for an article
 *
 * DOI (Digital Object Identifier) is a permanent identifier for academic articles.
 * The standard URL format is https://doi.org/[DOI]
 *
 * @param {{string}} doi - The DOI string
 * @returns {{string}} - The full DOI URL
 */
function getDoiUrl(doi) {{
  return `https://doi.org/${{doi}}`;
}}

/**
 * Extract publication venue (journal/conference) from article
 *
 * This function retrieves the container-title (journal name) from the article.
 *
 * @param {{object}} article - The article object from CrossRef
 * @returns {{string}} - The publication venue or "Unknown"
 */
function getPublicationVenue(article) {{
  if (article['container-title'] && article['container-title'].length > 0) {{
    return article['container-title'][0];
  }}
  return "Unknown";
}}

/**
 * Extract publication year from article
 *
 * CrossRef stores dates in various formats. This function attempts to extract
 * the year from the published date information.
 *
 * @param {{object}} article - The article object from CrossRef
 * @returns {{string}} - The publication year or "Unknown"
 */
function getPublicationYear(article) {{
  // Try published-print date first
  if (article['published-print'] && article['published-print']['date-parts']) {{
    const dateParts = article['published-print']['date-parts'][0];
    if (dateParts && dateParts.length > 0) {{
      return dateParts[0].toString();
    }}
  }}

  // Try published-online date
  if (article['published-online'] && article['published-online']['date-parts']) {{
    const dateParts = article['published-online']['date-parts'][0];
    if (dateParts && dateParts.length > 0) {{
      return dateParts[0].toString();
    }}
  }}

  // Try general published date
  if (article.published && article.published['date-parts']) {{
    const dateParts = article.published['date-parts'][0];
    if (dateParts && dateParts.length > 0) {{
      return dateParts[0].toString();
    }}
  }}

  return "Unknown";
}}

// ============================================================================
// TABULATOR TABLE CONFIGURATION FOR ARTICLES
// ============================================================================

/**
 * Tabulator table instance for articles
 * This variable will hold the Tabulator table object once initialized.
 * Named as specified: tableArticles
 */
let tableArticles;

/**
 * Initialize the Tabulator table for articles
 *
 * This function creates and configures the Tabulator table for displaying
 * article information with interactive features.
 */
function initializeArticlesTable() {{

  // Prepare the data with extracted and formatted fields
  const tableData = articles.map(article => ({{
    title: getArticleTitle(article),
    doi: article.DOI || '',
    type: article.type || 'Unknown',
    venue: getPublicationVenue(article),
    year: getPublicationYear(article),
    citations: article['is-referenced-by-count'] || 0
  }}));

  // Create the Tabulator table
  // The table is attached to the div with id "tableOfArticles"
  tableArticles = new Tabulator("#tableOfArticles", {{

    // DATA CONFIGURATION
    data: tableData,

    // LAYOUT CONFIGURATION
    layout: "fitColumns",
    responsiveLayout: "hide",

    // PAGINATION CONFIGURATION
    // Display 20 rows per page as specified
    pagination: true,
    paginationSize: 20,
    paginationSizeSelector: [10, 20, 50, 100],

    // INITIAL SORT
    // Sort by citation count (descending) so most cited articles appear first
    initialSort: [
      {{column: "citations", dir: "desc"}}
    ],

    // COLUMN DEFINITIONS
    columns: [
      {{
        title: "Article Title",
        field: "title",
        sorter: "string",
        headerFilter: "input",
        headerFilterPlaceholder: "Search title...",
        widthGrow: 4,
        // Format title as clickable link using DOI
        formatter: function(cell) {{
          const title = cell.getValue();
          const row = cell.getRow().getData();
          if (row.doi) {{
            const url = getDoiUrl(row.doi);
            return `<a href="${{url}}" target="_blank" rel="noopener noreferrer">${{title}}</a>`;
          }}
          return title;
        }},
        tooltip: true
      }},

      {{
        title: "Type",
        field: "type",
        sorter: "string",
        headerFilter: "input",
        headerFilterPlaceholder: "Filter type...",
        width: 150,
        tooltip: true
      }},

      {{
        title: "Where Published",
        field: "venue",
        sorter: "string",
        headerFilter: "input",
        headerFilterPlaceholder: "Search venue...",
        widthGrow: 2,
        tooltip: true
      }},

      {{
        title: "Year",
        field: "year",
        sorter: "number",
        headerFilter: "input",
        headerFilterPlaceholder: "Filter year...",
        width: 100,
        hozAlign: "center",
        headerHozAlign: "center"
      }},

      {{
        title: "Citations",
        field: "citations",
        sorter: "number",
        headerFilter: "input",
        headerFilterPlaceholder: "Filter citations...",
        width: 120,
        hozAlign: "center",
        headerHozAlign: "center"
      }}
    ]
  }});

  console.log("Articles table initialized with", tableData.length, "articles (2+ citations)");
}}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the table when the DOM is fully loaded
 */
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', initializeArticlesTable);
}} else {{
  initializeArticlesTable();
}}
'''

    # Save the JavaScript file for ARTICLES
    articles_js_filepath = "docs/js/table_articles.js"
    with open(articles_js_filepath, "w", encoding="utf-8") as f:
        f.write(articles_js_code)

    print(f"✓ Articles table JavaScript generated: {articles_js_filepath}")
    print(f"  Table contains {len(articles_filtered)} articles (2+ citations)")
    print()

    # ========================================================================
    # COMPLETION SUMMARY
    # ========================================================================

    print("=" * 80)
    print("✓ ALL TASKS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Summary of Results:")
    print(f"  • Total unique articles retrieved: {len(articles_list)}")
    print(f"  • Articles with abstracts: {count_with_abstract}")
    print(f"  • Articles with 2+ citations: {count_with_2plus_citations}")
    print(f"  • Unique journal titles (case-insensitive): {len(titles_list)}")
    print()
    print("Output Files Created:")
    print(f"  1. {output_filepath}")
    print(f"     - Complete article dataset with metadata")
    print(f"  2. {titles_filepath}")
    print(f"     - Journal titles with article counts (case-insensitive)")
    print(f"  3. {titles_js_filepath}")
    print(f"     - Interactive Tabulator table for journal titles")
    print(f"  4. {articles_js_filepath}")
    print(f"     - Interactive Tabulator table for articles (2+ citations)")
    print()
    print("Next Steps:")
    print("  • Review the generated JSON files")
    print("  • Integrate both Tabulator tables into your HTML file")
    print("  • See header comments in each .js file for integration instructions")
    print("  • Visit https://tabulator.info/docs/6.3 for Tabulator documentation")
    print("=" * 80)


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    Executes the main search_crossref() function.
    """
    search_crossref()
