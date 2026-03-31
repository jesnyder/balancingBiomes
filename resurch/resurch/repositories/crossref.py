"""CrossRef repository implementation."""

from typing import AsyncIterator, Optional, List
import httpx

from .base import BaseRepository, PaperResult, SearchProgress
from ..config import API_ENDPOINTS, RESULTS_PER_PAGE, RATE_LIMITS
from ..utils.rate_limiter import get_global_limiter
from ..utils.text import clean_text
from ..utils.doi import normalize_doi


class CrossRefRepository(BaseRepository):
    """CrossRef API repository."""

    name = "crossref"
    default_rate_limit = RATE_LIMITS.get("crossref", 1.0)

    def __init__(self):
        self.base_url = API_ENDPOINTS["crossref"]
        self.per_page = RESULTS_PER_PAGE.get("crossref", 20)

    async def search(
        self,
        query: str,
        max_results: int = 100,
        start_page: int = 0,
        cursor: Optional[str] = None,
    ) -> AsyncIterator[tuple[PaperResult, SearchProgress]]:
        """Search CrossRef for papers matching the query."""
        limiter = get_global_limiter()
        fetched = 0
        page = start_page
        total_results = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while fetched < max_results:
                await limiter.wait(self.name)

                offset = page * self.per_page
                params = {
                    "query": query,
                    "rows": min(self.per_page, max_results - fetched),
                    "offset": offset,
                }

                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                except (httpx.HTTPError, ValueError) as e:
                    # Log error but don't crash
                    break

                message = data.get("message", {})
                if total_results is None:
                    total_results = message.get("total-results", 0)

                items = message.get("items", [])
                if not items:
                    break

                for item in items:
                    paper = self._parse_item(item)
                    if paper:
                        fetched += 1
                        progress = SearchProgress(
                            current=fetched,
                            total=min(total_results, max_results) if total_results else None,
                            page=page,
                            is_complete=fetched >= max_results or fetched >= (total_results or max_results),
                        )
                        yield paper, progress

                        if fetched >= max_results:
                            break

                page += 1

                # Check if we've fetched all available results
                if len(items) < self.per_page:
                    break

    async def get_paper_details(self, identifier: str) -> Optional[PaperResult]:
        """Fetch detailed metadata for a paper by DOI."""
        doi = normalize_doi(identifier)
        if not doi:
            return None

        limiter = get_global_limiter()
        await limiter.wait(self.name)

        url = f"{self.base_url}/{doi}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return None
                data = response.json()
                return self._parse_item(data.get("message", {}))
            except (httpx.HTTPError, ValueError):
                return None

    def _parse_item(self, item: dict) -> Optional[PaperResult]:
        """Parse a CrossRef item into a PaperResult."""
        if not item:
            return None

        # Get title
        titles = item.get("title", [])
        title = titles[0] if titles else ""
        if not title:
            return None

        title = clean_text(title)

        # Get DOI
        doi = item.get("DOI")

        # Get abstract
        abstract = clean_text(item.get("abstract", ""))

        # Get year
        year = None
        published = item.get("published-print") or item.get("published-online") or item.get("created")
        if published:
            date_parts = published.get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

        # Get publication (container title)
        container = item.get("container-title", [])
        publication = container[0] if container else None

        # Get publisher
        publisher = item.get("publisher")

        # Get citation count
        citations = item.get("is-referenced-by-count", 0)

        # Get URLs
        doi_url = f"https://doi.org/{doi}" if doi else None
        publisher_url = item.get("URL")

        # Get PDF URL from links
        pdf_url = None
        links = item.get("link", [])
        for link in links:
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                break

        # Get authors
        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)

        return PaperResult(
            title=title,
            doi=doi,
            abstract=abstract,
            year=year,
            publication=publication,
            publisher=publisher,
            citations=citations,
            doi_url=doi_url,
            publisher_url=publisher_url,
            pdf_url=pdf_url,
            authors=authors,
            external_id=doi,
            raw_data=item,
        )
