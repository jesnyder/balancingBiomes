"""Semantic Scholar repository implementation."""

from typing import AsyncIterator, Optional, List
import httpx

from .base import BaseRepository, PaperResult, SearchProgress
from ..config import API_ENDPOINTS, RESULTS_PER_PAGE, RATE_LIMITS
from ..utils.rate_limiter import get_global_limiter
from ..utils.text import clean_text
from ..utils.doi import normalize_doi


class SemanticScholarRepository(BaseRepository):
    """Semantic Scholar API repository."""

    name = "semantic_scholar"
    default_rate_limit = RATE_LIMITS.get("semantic_scholar", 1.0)

    def __init__(self):
        self.base_url = API_ENDPOINTS["semantic_scholar"]
        self.per_page = RESULTS_PER_PAGE.get("semantic_scholar", 100)
        self.fields = "paperId,externalIds,title,abstract,year,venue,citationCount,url,openAccessPdf,authors"

    async def search(
        self,
        query: str,
        max_results: int = 100,
        start_page: int = 0,
        cursor: Optional[str] = None,
    ) -> AsyncIterator[tuple[PaperResult, SearchProgress]]:
        """Search Semantic Scholar for papers matching the query."""
        limiter = get_global_limiter()
        fetched = 0
        offset = start_page * self.per_page
        total_results = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while fetched < max_results:
                await limiter.wait(self.name)

                params = {
                    "query": query,
                    "limit": min(self.per_page, max_results - fetched),
                    "offset": offset,
                    "fields": self.fields,
                }

                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                except (httpx.HTTPError, ValueError) as e:
                    break

                if total_results is None:
                    total_results = data.get("total", 0)

                items = data.get("data", [])
                if not items:
                    break

                for item in items:
                    paper = self._parse_item(item)
                    if paper:
                        fetched += 1
                        progress = SearchProgress(
                            current=fetched,
                            total=min(total_results, max_results) if total_results else None,
                            page=offset // self.per_page,
                            is_complete=fetched >= max_results or fetched >= (total_results or max_results),
                        )
                        yield paper, progress

                        if fetched >= max_results:
                            break

                offset += len(items)

                # Check if we've fetched all available results
                if len(items) < self.per_page:
                    break

    async def get_paper_details(self, identifier: str) -> Optional[PaperResult]:
        """Fetch detailed metadata for a paper by DOI or Semantic Scholar ID."""
        limiter = get_global_limiter()
        await limiter.wait(self.name)

        # Try DOI first
        doi = normalize_doi(identifier)
        if doi:
            paper_id = f"DOI:{doi}"
        else:
            paper_id = identifier

        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        params = {"fields": self.fields}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    return None
                data = response.json()
                return self._parse_item(data)
            except (httpx.HTTPError, ValueError):
                return None

    def _parse_item(self, item: dict) -> Optional[PaperResult]:
        """Parse a Semantic Scholar item into a PaperResult."""
        if not item:
            return None

        # Get title
        title = item.get("title", "")
        if not title:
            return None

        title = clean_text(title)

        # Get DOI from external IDs
        doi = None
        external_ids = item.get("externalIds", {})
        if external_ids:
            doi = external_ids.get("DOI")

        # Get abstract
        abstract = clean_text(item.get("abstract", ""))

        # Get year
        year = item.get("year")

        # Get publication (venue)
        publication = item.get("venue")

        # Get citation count
        citations = item.get("citationCount", 0)

        # Get URLs
        doi_url = f"https://doi.org/{doi}" if doi else None
        publisher_url = item.get("url")

        # Get PDF URL
        pdf_url = None
        open_access = item.get("openAccessPdf")
        if open_access:
            pdf_url = open_access.get("url")

        # Get authors
        authors = []
        for author in item.get("authors", []):
            name = author.get("name")
            if name:
                authors.append(name)

        # Get Semantic Scholar ID
        external_id = item.get("paperId", "")

        return PaperResult(
            title=title,
            doi=doi,
            abstract=abstract if abstract else None,
            year=year,
            publication=publication,
            citations=citations,
            doi_url=doi_url,
            publisher_url=publisher_url,
            pdf_url=pdf_url,
            authors=authors,
            external_id=external_id,
            raw_data=item,
        )
