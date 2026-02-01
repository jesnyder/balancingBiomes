"""Search command implementation."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..database import session_scope, init_db
from ..models import Paper, PaperSource, Search
from ..repositories import get_repository, REPOSITORIES
from ..utils.progress import create_progress

console = Console()


def search_cmd(
    query: str = typer.Argument(..., help="Search query string."),
    where: List[str] = typer.Option(
        ["crossref"],
        "--where", "-w",
        help="Repository to search. Can be specified multiple times. Options: crossref, openalex, semantic_scholar, google_scholar"
    ),
    max_results: int = typer.Option(
        100, "--max", "-m",
        help="Maximum number of results per repository."
    ),
    resume: bool = typer.Option(
        False, "--resume", "-r",
        help="Resume an interrupted search."
    ),
):
    """
    Search academic repositories for papers.

    Examples:
        resurch search "halophyte AND halophile" --where crossref
        resurch search "machine learning" -w crossref -w openalex -m 50
    """
    init_db()
    asyncio.run(_search_async(query, where, max_results, resume))


def surch_cmd(
    query: str = typer.Argument(..., help="Search query string."),
    where: List[str] = typer.Option(
        ["crossref"],
        "--where", "-w",
        help="Repository to search."
    ),
    max_results: int = typer.Option(
        100, "--max", "-m",
        help="Maximum number of results per repository."
    ),
    resume: bool = typer.Option(
        False, "--resume", "-r",
        help="Resume an interrupted search."
    ),
):
    """Alias for search command."""
    search_cmd(query, where, max_results, resume)


async def _search_async(
    query: str,
    repositories: List[str],
    max_results: int,
    resume: bool,
):
    """Async search implementation."""
    console.print(f"\n[bold]Searching for:[/bold] {query}")
    console.print(f"[bold]Repositories:[/bold] {', '.join(repositories)}")
    console.print(f"[bold]Max results:[/bold] {max_results} per repository\n")

    total_added = 0
    total_updated = 0
    total_skipped = 0

    for repo_name in repositories:
        try:
            repo = get_repository(repo_name)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            continue

        console.print(f"\n[bold blue]Searching {repo.name}...[/bold blue]")

        # Check for existing search to resume
        start_page = 0
        cursor = None

        if resume:
            with session_scope() as session:
                existing_search = (
                    session.query(Search)
                    .filter(Search.query == query, Search.repository == repo.name)
                    .filter(Search.status.in_(["in_progress", "interrupted"]))
                    .order_by(Search.id.desc())
                    .first()
                )
                if existing_search:
                    start_page = existing_search.last_page
                    cursor = existing_search.cursor
                    console.print(f"  Resuming from page {start_page}")

        # Create or update search record
        with session_scope() as session:
            search_record = Search(
                query=query,
                repository=repo.name,
                status="in_progress",
                started_at=datetime.utcnow(),
            )
            session.add(search_record)
            session.flush()
            search_id = search_record.id

        added = 0
        updated = 0
        skipped = 0

        try:
            with create_progress() as progress:
                task = progress.add_task(f"[cyan]Fetching from {repo.name}...", total=max_results)

                async for paper, prog in repo.search(query, max_results, start_page, cursor):
                    # Save paper to database
                    result = _save_paper(paper, repo.name)
                    if result == "added":
                        added += 1
                    elif result == "updated":
                        updated += 1
                    else:
                        skipped += 1

                    # Update progress
                    progress.update(task, completed=prog.current)

                    # Update search record periodically
                    if prog.current % 10 == 0:
                        with session_scope() as session:
                            search = session.get(Search, search_id)
                            if search:
                                search.fetched_results = prog.current
                                search.last_page = prog.page
                                search.cursor = prog.cursor

            # Mark search as completed
            with session_scope() as session:
                search = session.get(Search, search_id)
                if search:
                    search.status = "completed"
                    search.completed_at = datetime.utcnow()
                    search.fetched_results = added + updated + skipped

        except KeyboardInterrupt:
            # Mark search as interrupted
            with session_scope() as session:
                search = session.get(Search, search_id)
                if search:
                    search.status = "interrupted"
            console.print("\n[yellow]Search interrupted. Use --resume to continue.[/yellow]")

        except Exception as e:
            # Mark search as failed
            with session_scope() as session:
                search = session.get(Search, search_id)
                if search:
                    search.status = "interrupted"
                    search.error_message = str(e)
            console.print(f"\n[red]Error during search:[/red] {e}")

        # Print summary for this repository
        console.print(f"  [green]Added:[/green] {added}")
        console.print(f"  [yellow]Updated:[/yellow] {updated}")
        console.print(f"  [dim]Skipped (duplicates):[/dim] {skipped}")

        total_added += added
        total_updated += updated
        total_skipped += skipped

    # Print overall summary
    console.print(f"\n[bold green]Search complete![/bold green]")
    console.print(f"  Total added: {total_added}")
    console.print(f"  Total updated: {total_updated}")
    console.print(f"  Total skipped: {total_skipped}")


def _save_paper(paper, repository: str) -> str:
    """
    Save a paper to the database.

    Returns:
        "added" if new paper was added
        "updated" if existing paper was updated
        "skipped" if paper already exists with same data
    """
    with session_scope() as session:
        existing = None

        # First try to find by DOI
        if paper.doi:
            existing = session.query(Paper).filter(Paper.doi == paper.doi).first()

        # If not found by DOI, try by title
        if not existing:
            # Use case-insensitive title matching
            existing = (
                session.query(Paper)
                .filter(Paper.title.ilike(paper.title))
                .first()
            )

        if existing:
            # Update if we have more data
            updated = False

            if paper.abstract and not existing.abstract:
                existing.abstract = paper.abstract
                updated = True
            if paper.doi and not existing.doi:
                existing.doi = paper.doi
                existing.doi_url = paper.doi_url
                updated = True
            if paper.year and not existing.year:
                existing.year = paper.year
                updated = True
            if paper.citations > existing.citations:
                existing.citations = paper.citations
                updated = True
            if paper.pdf_url and not existing.pdf_url:
                existing.pdf_url = paper.pdf_url
                updated = True

            # Add source record if not exists
            existing_source = (
                session.query(PaperSource)
                .filter(PaperSource.paper_id == existing.id, PaperSource.repository == repository)
                .first()
            )
            if not existing_source:
                source = PaperSource(
                    paper_id=existing.id,
                    repository=repository,
                    external_id=paper.external_id,
                    raw_data=json.dumps(paper.raw_data) if paper.raw_data else None,
                )
                session.add(source)
                updated = True

            return "updated" if updated else "skipped"

        else:
            # Create new paper
            new_paper = Paper(
                doi=paper.doi,
                title=paper.title,
                abstract=paper.abstract,
                snippet=paper.snippet,
                year=paper.year,
                publication=paper.publication,
                publisher=paper.publisher,
                citations=paper.citations,
                doi_url=paper.doi_url,
                publisher_url=paper.publisher_url,
                pdf_url=paper.pdf_url,
                authors=paper.authors_json,
            )
            session.add(new_paper)
            session.flush()

            # Add source record
            source = PaperSource(
                paper_id=new_paper.id,
                repository=repository,
                external_id=paper.external_id,
                raw_data=json.dumps(paper.raw_data) if paper.raw_data else None,
            )
            session.add(source)

            return "added"
