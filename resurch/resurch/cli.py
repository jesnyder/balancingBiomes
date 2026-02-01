"""Main CLI application using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .database import set_db_path

app = typer.Typer(
    name="resurch",
    help="Academic paper search and management CLI.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"resurch version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
    database: Optional[Path] = typer.Option(
        None, "--database", "-d",
        help="Path to SQLite database file. Defaults to resurch.db in current directory."
    ),
):
    """
    Resurch - Academic paper search and management CLI.

    Search academic repositories, store paper metadata in SQLite,
    and export/analyze your research database.
    """
    if database:
        set_db_path(database)


# Import and register subcommands
from .commands.search import search_cmd, surch_cmd
from .commands.enrich import enrich_cmd
from .commands.query import query_cmd
from .commands.export import export_cmd
from .commands.website import website_cmd, ssg_cmd, generate_cmd
from .commands.stats import stats_cmd, status_cmd, metrics_cmd

app.command(name="search", help="Search academic repositories for papers.")(search_cmd)
app.command(name="surch", help="Alias for search command.", hidden=True)(surch_cmd)
app.command(name="enrich", help="Enrich papers with missing metadata from APIs.")(enrich_cmd)
app.command(name="query", help="Query the paper database with SQL.")(query_cmd)
app.command(name="export", help="Export papers to CSV, JSON, or PDF.")(export_cmd)
app.command(name="website", help="Generate a static website from the database.")(website_cmd)
app.command(name="ssg", help="Alias for website command.", hidden=True)(ssg_cmd)
app.command(name="generate", help="Alias for website command.", hidden=True)(generate_cmd)
app.command(name="stats", help="Show database statistics.")(stats_cmd)
app.command(name="status", help="Alias for stats command.", hidden=True)(status_cmd)
app.command(name="metrics", help="Alias for stats command.", hidden=True)(metrics_cmd)


if __name__ == "__main__":
    app()
