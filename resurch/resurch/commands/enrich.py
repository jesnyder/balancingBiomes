"""Enrich command implementation."""

import asyncio
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console

from ..database import session_scope, init_db
from ..models import Paper, Enrichment
from ..repositories import get_repository
from ..config import ENRICHMENT_SOURCES
from ..utils.progress import create_progress

console = Console()


def enrich_cmd(
    enrichment_type: str = typer.Option(
        "abstract",
        "--type", "-t",
        help="Type of enrichment: abstract, doi, citations, pdf"
    ),
    sources: Optional[List[str]] = typer.Option(
        None,
        "--source", "-s",
        help="Sources to use for enrichment (default: crossref, openalex, semantic_scholar)"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Maximum number of papers to enrich"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Re-attempt previously failed enrichments"
    ),
):
    """
    Enrich papers with missing metadata from external APIs.

    Examples:
        resurch enrich --type abstract
        resurch enrich --type doi --source crossref --limit 50
        resurch enrich --type citations --force
    """
    init_db()

    if sources is None:
        sources = ENRICHMENT_SOURCES

    asyncio.run(_enrich_async(enrichment_type, sources, limit, force))


async def _enrich_async(
    enrichment_type: str,
    sources: List[str],
    limit: Optional[int],
    force: bool,
):
    """Async enrichment implementation."""
    console.print(f"\n[bold]Enrichment type:[/bold] {enrichment_type}")
    console.print(f"[bold]Sources:[/bold] {', '.join(sources)}")
    if limit:
        console.print(f"[bold]Limit:[/bold] {limit}")
    console.print()

    # Find papers needing enrichment
    papers = _get_papers_needing_enrichment(enrichment_type, limit, force)

    if not papers:
        console.print("[green]All papers are already enriched![/green]")
        return

    console.print(f"Found {len(papers)} papers to enrich.\n")

    enriched = 0
    failed = 0

    with create_progress() as progress:
        task = progress.add_task("[cyan]Enriching papers...", total=len(papers))

        for paper_id, paper_title, paper_doi in papers:
            result = await _enrich_paper(paper_id, paper_title, paper_doi, enrichment_type, sources)

            if result:
                enriched += 1
            else:
                failed += 1

            progress.update(task, advance=1)

    console.print(f"\n[bold green]Enrichment complete![/bold green]")
    console.print(f"  Enriched: {enriched}")
    console.print(f"  Failed: {failed}")


def _get_papers_needing_enrichment(
    enrichment_type: str,
    limit: Optional[int],
    force: bool,
) -> List[tuple]:
    """Get papers that need enrichment."""
    with session_scope() as session:
        query = session.query(Paper.id, Paper.title, Paper.doi)

        if enrichment_type == "abstract":
            # Papers without abstracts
            query = query.filter(
                (Paper.abstract.is_(None)) | (Paper.abstract == "")
            )
        elif enrichment_type == "doi":
            # Papers without DOIs
            query = query.filter(
                (Paper.doi.is_(None)) | (Paper.doi == "")
            )
        elif enrichment_type == "citations":
            # All papers (to update citation counts)
            pass
        elif enrichment_type == "pdf":
            # Papers without PDF URLs
            query = query.filter(
                (Paper.pdf_url.is_(None)) | (Paper.pdf_url == "")
            )

        if not force:
            # Exclude papers with failed enrichment of this type
            subquery = (
                session.query(Enrichment.paper_id)
                .filter(
                    Enrichment.enrichment_type == enrichment_type,
                    Enrichment.status == "failed"
                )
            )
            query = query.filter(~Paper.id.in_(subquery))

        if limit:
            query = query.limit(limit)

        return query.all()


async def _enrich_paper(
    paper_id: int,
    paper_title: str,
    paper_doi: Optional[str],
    enrichment_type: str,
    sources: List[str],
) -> bool:
    """Try to enrich a paper from available sources."""
    for source_name in sources:
        try:
            repo = get_repository(source_name)
        except ValueError:
            continue

        # Try to get paper details
        identifier = paper_doi if paper_doi else paper_title
        details = await repo.get_paper_details(identifier)

        if details:
            success = _apply_enrichment(paper_id, details, enrichment_type, source_name)
            if success:
                return True

    # Mark as failed if no source could enrich
    _mark_enrichment_failed(paper_id, enrichment_type)
    return False


def _apply_enrichment(
    paper_id: int,
    details,
    enrichment_type: str,
    source: str,
) -> bool:
    """Apply enrichment data to a paper."""
    with session_scope() as session:
        paper = session.get(Paper, paper_id)
        if not paper:
            return False

        updated = False

        if enrichment_type == "abstract" and details.abstract:
            paper.abstract = details.abstract
            updated = True

        elif enrichment_type == "doi" and details.doi:
            paper.doi = details.doi
            paper.doi_url = details.doi_url
            updated = True

        elif enrichment_type == "citations":
            if details.citations > paper.citations:
                paper.citations = details.citations
                updated = True

        elif enrichment_type == "pdf" and details.pdf_url:
            paper.pdf_url = details.pdf_url
            updated = True

        if updated:
            # Record successful enrichment
            enrichment = Enrichment(
                paper_id=paper_id,
                enrichment_type=enrichment_type,
                status="completed",
                source=source,
                attempted_at=datetime.utcnow(),
            )
            # Use merge to handle existing records
            session.merge(enrichment)

        return updated


def _mark_enrichment_failed(paper_id: int, enrichment_type: str):
    """Mark an enrichment attempt as failed."""
    with session_scope() as session:
        existing = (
            session.query(Enrichment)
            .filter(
                Enrichment.paper_id == paper_id,
                Enrichment.enrichment_type == enrichment_type
            )
            .first()
        )

        if existing:
            existing.status = "failed"
            existing.attempted_at = datetime.utcnow()
        else:
            enrichment = Enrichment(
                paper_id=paper_id,
                enrichment_type=enrichment_type,
                status="failed",
                attempted_at=datetime.utcnow(),
            )
            session.add(enrichment)
