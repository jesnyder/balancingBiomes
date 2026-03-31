"""DOI extraction and validation utilities."""

import re
from typing import Optional


def extract_doi_from_url(url: str) -> Optional[str]:
    """
    Extract DOI from a URL.

    DOI format: 10.XXXX/suffix
    - Prefix: 10. followed by 4-9 digits
    - Suffix: variable format (letters, numbers, periods, dashes)

    Handles:
    - DOI at end of URL
    - DOI in middle of URL
    - Removes .pdf, /full, /abstract suffixes

    Examples:
    - https://onlinelibrary.wiley.com/doi/abs/10.1002/9780470015902.a0000394.pub3
      -> 10.1002/9780470015902.a0000394.pub3
    - https://link.springer.com/content/pdf/10.1007/1-4020-4018-0.pdf
      -> 10.1007/1-4020-4018-0
    - https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2018.00148/full
      -> 10.3389/fmicb.2018.00148
    """
    if not url:
        return None

    # DOI regex patterns
    # Strict pattern: stops at common URL suffixes
    doi_pattern_strict = r'10\.\d{4,9}/[^\s"<>]+?(?=\.pdf|/full|\.html|/abstract|/pdf|\s|$|&|#|\?)'

    # Permissive pattern: captures more of the DOI
    doi_pattern_permissive = r'10\.\d{4,9}/[^\s"<>]+'

    # Try strict pattern first
    match = re.search(doi_pattern_strict, url)
    if match:
        doi = match.group(0)
    else:
        # Try permissive pattern
        match = re.search(doi_pattern_permissive, url)
        if match:
            doi = match.group(0)
        else:
            return None

    # Clean up the DOI
    doi = _clean_doi(doi)
    return doi if doi else None


def _clean_doi(doi: str) -> str:
    """Clean up extracted DOI by removing common suffixes."""
    # Remove trailing punctuation
    doi = doi.rstrip('.,;:)]}')

    # Remove common URL suffixes
    suffixes = ['.pdf', '/full', '/abstract', '/pdf', '.html']
    for suffix in suffixes:
        if doi.endswith(suffix):
            doi = doi[:-len(suffix)]

    # Remove trailing slash
    doi = doi.rstrip('/')

    return doi


def is_valid_doi(doi: str) -> bool:
    """Check if a string is a valid DOI format."""
    if not doi:
        return False
    pattern = r'^10\.\d{4,9}/[^\s]+$'
    return bool(re.match(pattern, doi))


def normalize_doi(doi: str) -> Optional[str]:
    """
    Normalize a DOI to a standard format.

    Handles:
    - Full URLs (https://doi.org/...)
    - doi: prefix
    - DOI: prefix
    - Bare DOIs
    """
    if not doi:
        return None

    doi = doi.strip()

    # Remove common prefixes
    prefixes = [
        'https://doi.org/',
        'http://doi.org/',
        'https://dx.doi.org/',
        'http://dx.doi.org/',
        'doi:',
        'DOI:',
        'doi: ',
        'DOI: ',
    ]

    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
            break

    # Try to extract DOI if it's still a URL
    if doi.startswith('http'):
        extracted = extract_doi_from_url(doi)
        if extracted:
            doi = extracted

    return doi if is_valid_doi(doi) else None


def doi_to_url(doi: str) -> str:
    """Convert a DOI to its canonical URL."""
    normalized = normalize_doi(doi)
    if normalized:
        return f"https://doi.org/{normalized}"
    return ""
