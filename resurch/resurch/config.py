"""Configuration constants and defaults."""

from pathlib import Path

# Default database location
DEFAULT_DB_PATH = Path("resurch.db")

# Rate limits (seconds between requests)
RATE_LIMITS = {
    "crossref": 1.0,
    "openalex": 0.5,
    "semantic_scholar": 1.0,
    "google_scholar": 70.0,  # Very aggressive rate limiting for Google Scholar
}

# Default max results per search
DEFAULT_MAX_RESULTS = 100

# Results per page for each repository
RESULTS_PER_PAGE = {
    "crossref": 20,
    "openalex": 25,
    "semantic_scholar": 100,
    "google_scholar": 10,
}

# User agent for requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

# API endpoints
API_ENDPOINTS = {
    "crossref": "https://api.crossref.org/works",
    "openalex": "https://api.openalex.org/works",
    "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
    "google_scholar": "https://scholar.google.com/scholar",
}

# Enrichment fallback order
ENRICHMENT_SOURCES = ["crossref", "openalex", "semantic_scholar"]
