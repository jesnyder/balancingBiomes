"""Text cleaning and HTML processing utilities."""

import re
import html
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Clean text field by removing HTML tags, format markers, and extra whitespace.

    Removes:
    - HTML tags like <b>, <i>, <em>, etc.
    - Format markers like [HTML], [PDF], [BOOK], [B]
    - Leading and trailing whitespace
    - HTML entities (&amp;, &lt;, etc.)
    - Multiple consecutive spaces
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove HTML tags (anything between < and >)
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities (&amp; -> &, &lt; -> <, etc.)
    text = html.unescape(text)

    # Remove format markers like [HTML], [PDF], [BOOK], [B], [XML], [DOC], [CITATION]
    text = re.sub(r'\[(?:HTML|PDF|BOOK|B|XML|DOC|CITATION)\]', '', text, flags=re.IGNORECASE)

    # Remove extra whitespace (multiple spaces, newlines, tabs)
    text = ' '.join(text.split())

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_title(title: str) -> str:
    """Normalize a title for comparison (case-insensitive, stripped)."""
    return clean_text(title).upper().strip()


def extract_year_from_text(text: str) -> Optional[int]:
    """Try to extract a 4-digit year from text."""
    if not text:
        return None

    # Look for 4-digit years between 1900 and 2099
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    if match:
        return int(match.group(1))
    return None


def invert_abstract_index(inverted_index: dict) -> str:
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

    # Find the maximum position
    max_position = 0
    for positions in inverted_index.values():
        if positions:
            max_position = max(max_position, max(positions))

    # Initialize word array
    words = [''] * (max_position + 1)

    # Place each word at its positions
    for word, positions in inverted_index.items():
        for pos in positions:
            if 0 <= pos < len(words):
                words[pos] = word

    # Join words into text
    abstract = ' '.join(words)

    return abstract
