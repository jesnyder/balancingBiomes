"""Export command implementation."""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..database import session_scope, init_db
from ..models import Paper

console = Console()
stderr_console = Console(stderr=True)


def export_cmd(
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path. Defaults to stdout."
    ),
    format: str = typer.Option(
        "csv",
        "--format", "-f",
        help="Output format: csv, json"
    ),
    min_citations: int = typer.Option(
        0,
        "--min-citations", "-c",
        help="Minimum citation count to include"
    ),
    has_abstract: bool = typer.Option(
        False,
        "--has-abstract", "-a",
        help="Only include papers with abstracts"
    ),
    has_doi: bool = typer.Option(
        False,
        "--has-doi", "-d",
        help="Only include papers with DOIs"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Maximum number of papers to export"
    ),
):
    """
    Export papers to CSV or JSON.

    Examples:
        resurch export -f csv > papers.csv
        resurch export -f json -o papers.json
        resurch export --min-citations 10 --has-doi -o top_papers.csv
    """
    init_db()

    # Get papers from database
    papers = _get_papers(min_citations, has_abstract, has_doi, limit)

    if not papers:
        stderr_console.print("[yellow]No papers to export.[/yellow]")
        return

    stderr_console.print(f"[dim]Exporting {len(papers)} papers...[/dim]")

    # Determine output
    if output:
        # Infer format from extension if not explicitly set
        if format == "csv" and output.suffix.lower() == ".json":
            format = "json"
        elif format == "json" and output.suffix.lower() == ".csv":
            format = "csv"

    if format == "csv":
        content = _export_csv(papers)
    elif format == "json":
        content = _export_json(papers)
    else:
        stderr_console.print(f"[red]Unknown format: {format}[/red]")
        return

    # Write output
    if output:
        output.write_text(content, encoding="utf-8")
        stderr_console.print(f"[green]Exported to {output}[/green]")
    else:
        print(content)


def _get_papers(
    min_citations: int,
    has_abstract: bool,
    has_doi: bool,
    limit: Optional[int],
) -> list:
    """Get papers matching filter criteria."""
    with session_scope() as session:
        query = session.query(Paper)

        if min_citations > 0:
            query = query.filter(Paper.citations >= min_citations)

        if has_abstract:
            query = query.filter(
                Paper.abstract.isnot(None),
                Paper.abstract != ""
            )

        if has_doi:
            query = query.filter(
                Paper.doi.isnot(None),
                Paper.doi != ""
            )

        query = query.order_by(Paper.citations.desc())

        if limit:
            query = query.limit(limit)

        # Convert to dicts to avoid session issues
        papers = []
        for paper in query.all():
            papers.append({
                "id": paper.id,
                "doi": paper.doi,
                "title": paper.title,
                "abstract": paper.abstract,
                "snippet": paper.snippet,
                "year": paper.year,
                "publication": paper.publication,
                "publisher": paper.publisher,
                "citations": paper.citations,
                "doi_url": paper.doi_url,
                "publisher_url": paper.publisher_url,
                "pdf_url": paper.pdf_url,
                "authors": paper.authors,
            })

        return papers


def _export_csv(papers: list) -> str:
    """Export papers to CSV string."""
    import io

    output = io.StringIO()
    fieldnames = [
        "id", "doi", "title", "abstract", "year", "publication",
        "publisher", "citations", "doi_url", "publisher_url", "pdf_url", "authors"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(papers)

    return output.getvalue()


def _export_json(papers: list) -> str:
    """Export papers to JSON string."""
    return json.dumps(
        {
            "count": len(papers),
            "papers": papers,
        },
        indent=2,
        ensure_ascii=False,
    )
