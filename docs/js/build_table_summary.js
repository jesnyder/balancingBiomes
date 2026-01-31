
/**
 * ==========================================================
 * SEARCH SUMMARY TABLE
 * ==========================================================
 *
 * INSTRUCTIONS:
 *
 * 1. Include Tabulator CSS and JS in your index.html (in <head> or before </body>):
 *    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
 *    <script src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>
 *
 * 2. Add this HTML in your index.html body where you want the table:
 *    <button id="download-table-data">Download Table Data</button>
 *    <div id="table_search_summary"></div>
 *
 * 3. Load this JS file AFTER the div/button:
 *    <script src="js/build_table_summary.js"></script>
 *
 * WHY:
 * - Data is hardcoded to allow client-side rendering without backend.
 * - Tabulator provides dynamic sorting, filtering, and CSV export.
 * - Column header filters allow searching each column individually.
 * - Hyperlinks in the table will open safely in a new tab.
 * - Pagination is set to display all rows so the full table is visible.
 *
 * ==========================================================
 */

 // -------------------------------
 // 4a. Hardcoded table data
 // -------------------------------
const table_summary_data = [
  {
    "database": "list_openalex",
    "num_results": 354,
    "fields_captured": "abstract_inverted_index, apc_list, apc_paid, authors, authorships, awards, best_oa_location, biblio, citation_normalized_percentile, citations, cited_by, cited_by_count, cited_by_percentile_year, concepts, corresponding_author_ids, corresponding_institution_ids, countries_distinct_count, counts_by_year, created_date, databases_found_in, display_name, doi, doiURL, funders, fwci, has_content, has_fulltext, id, ids, indexed_in, institutions, institutions_distinct_count, is_paratext, is_referenced_by_count, is_retracted, is_xpac, keywords, language, locations, locations_count, mesh, open_access, paperId, primary_location, primary_topic, publication_date, publication_info, publication_year, publisher, reference_count, referenced_works, referenced_works_count, related_articles, related_works, relevance_score, snippet, sustainable_development_goals, title, title_link, topics, type, updated_date, url, year",
    "in_list_openalex": 354,
    "in_list_crossref": 15,
    "in_list_semanticscholar": 18,
    "in_list_gscholar": 59
  },
  {
    "database": "list_crossref",
    "num_results": 2386,
    "fields_captured": "authors, citations, cited_by, databases_found_in, doi, is_referenced_by_count, paperId, publication_info, publication_year, publisher, reference_count, related_articles, snippet, title, title_link, type, url, year",
    "in_list_openalex": 17,
    "in_list_crossref": 2386,
    "in_list_semanticscholar": 7,
    "in_list_gscholar": 41
  },
  {
    "database": "list_semanticscholar",
    "num_results": 34,
    "fields_captured": "authors, citations, cited_by, databases_found_in, doi, paperId, publication_info, publication_year, related_articles, snippet, title, title_link, url, year",
    "in_list_openalex": 4,
    "in_list_crossref": 0,
    "in_list_semanticscholar": 34,
    "in_list_gscholar": 12
  },
  {
    "database": "list_gscholar",
    "num_results": 490,
    "fields_captured": "citations, cited_by, databases_found_in, doi, publication_info, publication_year, related_articles, snippet, title, title_link, url",
    "in_list_openalex": 1,
    "in_list_crossref": 0,
    "in_list_semanticscholar": 12,
    "in_list_gscholar": 490
  }
];

 // -------------------------------
 // 4b. Create Tabulator table
 // -------------------------------
const table_search_summary = new Tabulator("#table_search_summary", {
    data: table_summary_data,           // Load the hardcoded data
    layout: "fitColumns",               // Adjust columns to fit the table width
    pagination: "local",                // Enable pagination
    paginationSize: table_summary_data.length, // Show all rows on one page
    movableColumns: true,               // Allow columns to be reordered
    height: "600px",                    // Fixed height with scroll if needed
    columns: Object.keys(table_summary_data[0] || {}).map(key => {
        return {
            // Convert column keys to human-readable titles
            title: key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase()),
            field: key,
            headerFilter: "input",      // Adds a search input below the header
            formatter: function(cell) {
                // Detect if value looks like a URL and render as hyperlink
                const val = cell.getValue();
                const urlPattern = /^https?:\/\//i;
                if (val && typeof val === "string" && urlPattern.test(val)) {
                    return `<a href="${val}" target="_blank" rel="noopener noreferrer">${val}</a>`;
                }
                return val;
            }
        };
    })
});

 // -------------------------------
 // 4c. Add CSV download functionality
 // -------------------------------
document.getElementById("download-table-data").addEventListener("click", function() {
    table_search_summary.download("csv", "search_summary_table.csv");
});
