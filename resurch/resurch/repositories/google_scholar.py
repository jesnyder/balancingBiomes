"""Google Scholar repository implementation (web scraping)."""

from typing import AsyncIterator, Optional, List
import re
import httpx
from bs4 import BeautifulSoup

from .base import BaseRepository, PaperResult, SearchProgress
from ..config import API_ENDPOINTS, RESULTS_PER_PAGE, RATE_LIMITS, USER_AGENT
from ..utils.rate_limiter import get_global_limiter
from ..utils.text import clean_text, extract_year_from_text
from ..utils.doi import extract_doi_from_url


class GoogleScholarRepository(BaseRepository):
    """Google Scholar web scraping repository.

    WARNING: Google Scholar is very aggressive about rate limiting.
    Use with caution and respect their terms of service.
    """

    name = "google_scholar"
    default_rate_limit = RATE_LIMITS.get("google_scholar", 70.0)

    def __init__(self):
        self.base_url = API_ENDPOINTS["google_scholar"]
        self.per_page = RESULTS_PER_PAGE.get("google_scholar", 10)

    async def search(
        self,
        query: str,
        max_results: int = 100,
        start_page: int = 0,
        cursor: Optional[str] = None,
    ) -> AsyncIterator[tuple[PaperResult, SearchProgress]]:
        """Search Google Scholar for papers matching the query."""
        limiter = get_global_limiter()
        fetched = 0
        page = start_page

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            while fetched < max_results:
                await limiter.wait(self.name)

                start_index = page * self.per_page
                params = {
                    "q": query,
                    "hl": "en",
                    "start": start_index,
                }

                try:
                    response = await client.get(self.base_url, params=params, headers=headers)

                    # Check for rate limiting
                    if response.status_code == 429:
                        # Rate limited - stop
                        break
                    elif response.status_code in [503, 403]:
                        # Blocked or forbidden - stop
                        break
                    elif response.status_code != 200:
                        break

                    html_content = response.text
                except httpx.HTTPError as e:
                    break

                # Parse the HTML
                papers = self._parse_html(html_content)
                if not papers:
                    break

                for paper in papers:
                    fetched += 1
                    progress = SearchProgress(
                        current=fetched,
                        total=None,  # Google Scholar doesn't provide total count reliably
                        page=page,
                        is_complete=fetched >= max_results,
                    )
                    yield paper, progress

                    if fetched >= max_results:
                        break

                page += 1

                # If we got fewer than expected, we've likely reached the end
                if len(papers) < self.per_page:
                    break

    async def get_paper_details(self, identifier: str) -> Optional[PaperResult]:
        """
        Google Scholar doesn't have a direct paper lookup API.
        Return None - enrichment should use other sources.
        """
        return None

    def _parse_html(self, html_content: str) -> List[PaperResult]:
        """Parse Google Scholar HTML response."""
        papers = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Google Scholar lists articles in <div class="gs_ri">
        for div in soup.find_all("div", class_="gs_ri"):
            paper = self._parse_result_div(div)
            if paper:
                papers.append(paper)

        return papers

    def _parse_result_div(self, div) -> Optional[PaperResult]:
        """Parse a single result div from Google Scholar."""
        # Get title and link
        title = ""
        publisher_url = ""
        title_tag = div.find("h3", class_="gs_rt")
        if title_tag:
            title = clean_text(title_tag.get_text())
            link_tag = title_tag.find("a")
            if link_tag:
                publisher_url = link_tag.get("href", "")

        if not title:
            return None

        # Get author/year info
        year = None
        authors = []
        author_year_tag = div.find("div", class_="gs_a")
        if author_year_tag:
            text = author_year_tag.get_text()
            year = extract_year_from_text(text)

            # Try to extract authors (everything before the first " - ")
            parts = text.split(" - ")
            if parts:
                author_text = parts[0]
                # Split by comma and clean
                for author in author_text.split(","):
                    author = author.strip()
                    # Skip things that look like years or ellipsis
                    if author and not author.isdigit() and author != "...":
                        authors.append(author)

        # Get snippet
        snippet = ""
        snippet_tag = div.find("div", class_="gs_rs")
        if snippet_tag:
            snippet = clean_text(snippet_tag.get_text())

        # Get citation count
        citations = 0
        cite_tag = div.find("div", class_="gs_fl")
        if cite_tag:
            cite_links = cite_tag.find_all("a")
            for link in cite_links:
                text = link.get_text()
                if "Cited by" in text:
                    match = re.search(r"Cited by (\d+)", text)
                    if match:
                        citations = int(match.group(1))
                    break

        # Try to extract DOI from publisher URL
        doi = None
        doi_url = None
        if publisher_url:
            doi = extract_doi_from_url(publisher_url)
            if doi:
                doi_url = f"https://doi.org/{doi}"

        # Look for PDF link
        pdf_url = None
        parent = div.parent
        if parent:
            pdf_div = parent.find("div", class_="gs_or_ggsm")
            if pdf_div:
                pdf_link = pdf_div.find("a")
                if pdf_link:
                    pdf_url = pdf_link.get("href", "")

        return PaperResult(
            title=title,
            doi=doi,
            snippet=snippet,
            year=year,
            citations=citations,
            doi_url=doi_url,
            publisher_url=publisher_url,
            pdf_url=pdf_url,
            authors=authors,
        )
