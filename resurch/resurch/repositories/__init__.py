"""Repository implementations for academic paper sources."""

from .base import BaseRepository, PaperResult, SearchProgress
from .crossref import CrossRefRepository
from .openalex import OpenAlexRepository
from .semantic_scholar import SemanticScholarRepository
from .google_scholar import GoogleScholarRepository

# Registry of available repositories
REPOSITORIES: dict[str, type[BaseRepository]] = {
    "crossref": CrossRefRepository,
    "openalex": OpenAlexRepository,
    "semantic_scholar": SemanticScholarRepository,
    "google_scholar": GoogleScholarRepository,
}


def get_repository(name: str) -> BaseRepository:
    """Get a repository instance by name."""
    name = name.lower().replace("-", "_").replace(" ", "_")
    if name not in REPOSITORIES:
        raise ValueError(f"Unknown repository: {name}. Available: {list(REPOSITORIES.keys())}")
    return REPOSITORIES[name]()


__all__ = [
    "BaseRepository",
    "PaperResult",
    "SearchProgress",
    "CrossRefRepository",
    "OpenAlexRepository",
    "SemanticScholarRepository",
    "GoogleScholarRepository",
    "REPOSITORIES",
    "get_repository",
]
