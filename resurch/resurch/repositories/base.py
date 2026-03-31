"""Base repository interface and common data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional, List
import json


@dataclass
class PaperResult:
    """Standardized paper result from any repository."""

    title: str
    doi: Optional[str] = None
    abstract: Optional[str] = None
    snippet: Optional[str] = None
    year: Optional[int] = None
    publication: Optional[str] = None
    publisher: Optional[str] = None
    citations: int = 0
    doi_url: Optional[str] = None
    publisher_url: Optional[str] = None
    pdf_url: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    external_id: Optional[str] = None
    raw_data: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "title": self.title,
            "doi": self.doi,
            "abstract": self.abstract,
            "snippet": self.snippet,
            "year": self.year,
            "publication": self.publication,
            "publisher": self.publisher,
            "citations": self.citations,
            "doi_url": self.doi_url,
            "publisher_url": self.publisher_url,
            "pdf_url": self.pdf_url,
            "authors": json.dumps(self.authors) if self.authors else None,
        }

    @property
    def authors_json(self) -> str:
        """Get authors as JSON string."""
        return json.dumps(self.authors) if self.authors else "[]"


@dataclass
class SearchProgress:
    """Progress information for a search operation."""

    current: int
    total: Optional[int] = None
    page: int = 0
    cursor: Optional[str] = None
    is_complete: bool = False

    @property
    def percentage(self) -> Optional[float]:
        """Get completion percentage if total is known."""
        if self.total and self.total > 0:
            return (self.current / self.total) * 100
        return None


class BaseRepository(ABC):
    """Abstract base class for paper repositories."""

    name: str = "base"
    default_rate_limit: float = 1.0

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 100,
        start_page: int = 0,
        cursor: Optional[str] = None,
    ) -> AsyncIterator[tuple[PaperResult, SearchProgress]]:
        """
        Search for papers matching the query.

        Yields (paper, progress) tuples for immediate persistence.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            start_page: Page number to start from (for resuming)
            cursor: Optional cursor for APIs that use cursor-based pagination

        Yields:
            Tuple of (PaperResult, SearchProgress)
        """
        pass

    @abstractmethod
    async def get_paper_details(self, identifier: str) -> Optional[PaperResult]:
        """
        Fetch detailed metadata for a specific paper.

        Args:
            identifier: DOI or other identifier

        Returns:
            PaperResult with full metadata or None if not found
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
