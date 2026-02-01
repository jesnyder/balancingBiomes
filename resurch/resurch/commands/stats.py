"""Stats command implementation."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import func

from ..database import session_scope, init_db
from ..models import Paper, PaperSource, Search, Enrichment

console = Console()


def stats_cmd():
    """
    Show database statistics.

    Displays summary information about papers, sources, searches, and enrichments.
    """
    init_db()
    _show_stats()


def status_cmd():
    """Alias for stats command."""
    stats_cmd()


def metrics_cmd():
    """Alias for stats command."""
    stats_cmd()


def _show_stats():
    """Display database statistics."""
    with session_scope() as session:
        # Paper statistics
        total_papers = session.query(func.count(Paper.id)).scalar()
        with_doi = session.query(func.count(Paper.id)).filter(
            Paper.doi.isnot(None), Paper.doi != ""
        ).scalar()
        with_abstract = session.query(func.count(Paper.id)).filter(
            Paper.abstract.isnot(None), Paper.abstract != ""
        ).scalar()
        with_pdf = session.query(func.count(Paper.id)).filter(
            Paper.pdf_url.isnot(None), Paper.pdf_url != ""
        ).scalar()
        total_citations = session.query(func.sum(Paper.citations)).scalar() or 0
        avg_citations = session.query(func.avg(Paper.citations)).scalar() or 0
        max_citations = session.query(func.max(Paper.citations)).scalar() or 0

        # Year range
        min_year = session.query(func.min(Paper.year)).filter(Paper.year.isnot(None)).scalar()
        max_year = session.query(func.max(Paper.year)).filter(Paper.year.isnot(None)).scalar()

        # Source statistics
        sources = (
            session.query(PaperSource.repository, func.count(PaperSource.id))
            .group_by(PaperSource.repository)
            .all()
        )

        # Search statistics
        total_searches = session.query(func.count(Search.id)).scalar()
        completed_searches = session.query(func.count(Search.id)).filter(
            Search.status == "completed"
        ).scalar()
        interrupted_searches = session.query(func.count(Search.id)).filter(
            Search.status == "interrupted"
        ).scalar()

        # Enrichment statistics
        total_enrichments = session.query(func.count(Enrichment.id)).scalar()
        completed_enrichments = session.query(func.count(Enrichment.id)).filter(
            Enrichment.status == "completed"
        ).scalar()
        failed_enrichments = session.query(func.count(Enrichment.id)).filter(
            Enrichment.status == "failed"
        ).scalar()

    # Display paper stats
    console.print("\n[bold blue]Paper Statistics[/bold blue]")
    console.print("=" * 40)

    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Total papers", str(total_papers))
    table.add_row("With DOI", f"{with_doi} ({_pct(with_doi, total_papers)})")
    table.add_row("With abstract", f"{with_abstract} ({_pct(with_abstract, total_papers)})")
    table.add_row("With PDF URL", f"{with_pdf} ({_pct(with_pdf, total_papers)})")
    table.add_row("", "")
    table.add_row("Total citations", f"{total_citations:,}")
    table.add_row("Average citations", f"{avg_citations:.1f}")
    table.add_row("Max citations", f"{max_citations:,}")
    table.add_row("", "")
    if min_year and max_year:
        table.add_row("Year range", f"{min_year} - {max_year}")

    console.print(table)

    # Display source stats
    if sources:
        console.print("\n[bold blue]Papers by Source[/bold blue]")
        console.print("=" * 40)

        source_table = Table(show_header=True)
        source_table.add_column("Repository")
        source_table.add_column("Papers", justify="right")

        for repo, count in sorted(sources, key=lambda x: x[1], reverse=True):
            source_table.add_row(repo, str(count))

        console.print(source_table)

    # Display search stats
    if total_searches > 0:
        console.print("\n[bold blue]Search Statistics[/bold blue]")
        console.print("=" * 40)

        search_table = Table(show_header=False, box=None)
        search_table.add_column("Metric", style="dim")
        search_table.add_column("Value", justify="right")

        search_table.add_row("Total searches", str(total_searches))
        search_table.add_row("Completed", str(completed_searches))
        search_table.add_row("Interrupted", str(interrupted_searches))

        console.print(search_table)

    # Display enrichment stats
    if total_enrichments > 0:
        console.print("\n[bold blue]Enrichment Statistics[/bold blue]")
        console.print("=" * 40)

        enrich_table = Table(show_header=False, box=None)
        enrich_table.add_column("Metric", style="dim")
        enrich_table.add_column("Value", justify="right")

        enrich_table.add_row("Total enrichments", str(total_enrichments))
        enrich_table.add_row("Completed", str(completed_enrichments))
        enrich_table.add_row("Failed", str(failed_enrichments))

        console.print(enrich_table)

    console.print()


def _pct(part: int, total: int) -> str:
    """Calculate percentage string."""
    if total == 0:
        return "0%"
    return f"{(part / total) * 100:.1f}%"
