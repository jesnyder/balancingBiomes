"""OpenAlex repository implementation."""

from typing import AsyncIterator, Optional, List
import httpx

from .base import BaseRepository, PaperResult, SearchProgress
from ..config import API_ENDPOINTS, RESULTS_PER_PAGE, RATE_LIMITS
from ..utils.rate_limiter import get_global_limiter
from ..utils.text import clean_text, invert_abstract_index
from ..utils.doi import normalize_doi


class OpenAlexRepository(BaseRepository):
    """OpenAlex API repository."""

    name = "openalex"
    default_rate_limit = RATE_LIMITS.get("openalex", 0.5)

    def __init__(self):
        self.base_url = API_ENDPOINTS["openalex"]
        self.per_page = RESULTS_PER_PAGE.get("openalex", 25)

    async def search(
        self,
        query: str,
        max_results: int = 100,
        start_page: int = 0,
        cursor: Optional[str] = None,
    ) -> AsyncIterator[tuple[PaperResult, SearchProgress]]:
        """Search OpenAlex for papers matching the query."""
        limiter = get_global_limiter()
        fetched = 0
        page = start_page + 1  # OpenAlex uses 1-based pages
        total_results = None
        current_cursor = cursor

        async with httpx.AsyncClient(timeout=30.0) as client:
            while fetched < max_results:
                await limiter.wait(self.name)

                params = {
                    "search": query,
                    "per-page": min(self.per_page, max_results - fetched),
                }

                # Use cursor if available, otherwise use page
                if current_cursor:
                    params["cursor"] = current_cursor
                else:
                    params["page"] = page

                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                except (httpx.HTTPError, ValueError) as e:
                    break

                meta = data.get("meta", {})
                if total_results is None:
                    total_results = meta.get("count", 0)

                # Get next cursor for pagination
                current_cursor = meta.get("next_cursor")

                results = data.get("results", [])
                if not results:
                    break

                for item in results:
                    paper = self._parse_item(item)
                    if paper:
                        fetched += 1
                        progress = SearchProgress(
                            current=fetched,
                            total=min(total_results, max_results) if total_results else None,
                            page=page,
                            cursor=current_cursor,
                            is_complete=fetched >= max_results or fetched >= (total_results or max_results),
                        )
                        yield paper, progress

                        if fetched >= max_results:
                            break

                page += 1

                # Check if we've fetched all available results
                if len(results) < self.per_page or not current_cursor:
                    break

    async def get_paper_details(self, identifier: str) -> Optional[PaperResult]:
        """Fetch detailed metadata for a paper by DOI."""
        doi = normalize_doi(identifier)
        if not doi:
            return None

        limiter = get_global_limiter()
        await limiter.wait(self.name)

        url = f"{self.base_url}/doi:{doi}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return None
                data = response.json()
                return self._parse_item(data)
            except (httpx.HTTPError, ValueError):
                return None

    def _parse_item(self, item: dict) -> Optional[PaperResult]:
        """Parse an OpenAlex item into a PaperResult."""
        if not item:
            return None

        # Get title
        title = item.get("title", "")
        if not title:
            return None

        title = clean_text(title)

        # Get DOI
        doi = item.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[16:]

        # Get abstract from inverted index
        abstract = ""
        abstract_inverted_index = item.get("abstract_inverted_index")
        if abstract_inverted_index:
            abstract = invert_abstract_index(abstract_inverted_index)
            abstract = clean_text(abstract)

        # Get year
        year = item.get("publication_year")

        # Get publication (primary location)
        publication = None
        primary_location = item.get("primary_location", {})
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                publication = source.get("display_name")

        # Get publisher
        publisher = None
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                publisher = source.get("host_organization_name")

        # Get citation count
        citations = item.get("cited_by_count", 0)

        # Get URLs
        doi_url = item.get("doi")
        publisher_url = None
        if primary_location:
            publisher_url = primary_location.get("landing_page_url")

        # Get PDF URL
        pdf_url = None
        if primary_location:
            pdf_url = primary_location.get("pdf_url")
        if not pdf_url:
            # Check open access locations
            oa_locations = item.get("open_access", {}).get("oa_locations", [])
            for loc in oa_locations:
                if loc.get("pdf_url"):
                    pdf_url = loc.get("pdf_url")
                    break

        # Get authors
        authors = []
        for authorship in item.get("authorships", []):
            author_info = authorship.get("author", {})
            name = author_info.get("display_name")
            if name:
                authors.append(name)

        # Get OpenAlex ID
        external_id = item.get("id", "")

        return PaperResult(
            title=title,
            doi=doi if doi else None,
            abstract=abstract if abstract else None,
            year=year,
            publication=publication,
            publisher=publisher,
            citations=citations,
            doi_url=doi_url,
            publisher_url=publisher_url,
            pdf_url=pdf_url,
            authors=authors,
            external_id=external_id,
            raw_data=item,
        )
