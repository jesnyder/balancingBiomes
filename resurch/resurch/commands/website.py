"""Website (static site generator) command implementation."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from jinja2 import Environment, FileSystemLoader, PackageLoader

from ..database import session_scope, init_db
from ..models import Paper

console = Console()


def website_cmd(
    output: Path = typer.Option(
        Path("./site"),
        "--output", "-o",
        help="Output directory for generated site."
    ),
    title: str = typer.Option(
        "Research Papers",
        "--title", "-t",
        help="Site title."
    ),
    min_citations: int = typer.Option(
        0,
        "--min-citations", "-c",
        help="Minimum citation count to include."
    ),
):
    """
    Generate a static website from the database.

    Creates an interactive HTML page with Tabulator.js for filtering and sorting.

    Examples:
        resurch website -o ./docs
        resurch website --title "Halophyte Research" --min-citations 2
    """
    init_db()
    _generate_website(output, title, min_citations)


def ssg_cmd(
    output: Path = typer.Option(
        Path("./site"),
        "--output", "-o",
        help="Output directory for generated site."
    ),
    title: str = typer.Option(
        "Research Papers",
        "--title", "-t",
        help="Site title."
    ),
    min_citations: int = typer.Option(
        0,
        "--min-citations", "-c",
        help="Minimum citation count to include."
    ),
):
    """Alias for website command."""
    website_cmd(output, title, min_citations)


def generate_cmd(
    output: Path = typer.Option(
        Path("./site"),
        "--output", "-o",
        help="Output directory for generated site."
    ),
    title: str = typer.Option(
        "Research Papers",
        "--title", "-t",
        help="Site title."
    ),
    min_citations: int = typer.Option(
        0,
        "--min-citations", "-c",
        help="Minimum citation count to include."
    ),
):
    """Alias for website command."""
    website_cmd(output, title, min_citations)


def _generate_website(output: Path, title: str, min_citations: int):
    """Generate the static website."""
    # Create output directory
    output.mkdir(parents=True, exist_ok=True)
    (output / "js").mkdir(exist_ok=True)
    (output / "css").mkdir(exist_ok=True)

    # Get papers
    papers = _get_papers_for_website(min_citations)

    if not papers:
        console.print("[yellow]No papers to include in website.[/yellow]")
        return

    console.print(f"Generating website with {len(papers)} papers...")

    # Get statistics
    stats = _get_stats(papers)

    # Generate HTML
    html_content = _generate_html(title, papers, stats)
    (output / "index.html").write_text(html_content, encoding="utf-8")

    # Generate JavaScript data file
    js_content = _generate_js_data(papers)
    (output / "js" / "papers.js").write_text(js_content, encoding="utf-8")

    # Generate CSS
    css_content = _generate_css()
    (output / "css" / "style.css").write_text(css_content, encoding="utf-8")

    console.print(f"[green]Website generated at {output}[/green]")
    console.print(f"[dim]Open {output}/index.html in a browser to view.[/dim]")


def _get_papers_for_website(min_citations: int) -> list:
    """Get papers for the website."""
    with session_scope() as session:
        query = session.query(Paper)

        if min_citations > 0:
            query = query.filter(Paper.citations >= min_citations)

        query = query.order_by(Paper.citations.desc())

        papers = []
        for paper in query.all():
            papers.append({
                "id": paper.id,
                "doi": paper.doi or "",
                "title": paper.title or "",
                "abstract": (paper.abstract or "")[:500] + "..." if paper.abstract and len(paper.abstract) > 500 else (paper.abstract or ""),
                "year": paper.year,
                "publication": paper.publication or "",
                "citations": paper.citations or 0,
                "doi_url": paper.doi_url or "",
                "pdf_url": paper.pdf_url or "",
            })

        return papers


def _get_stats(papers: list) -> dict:
    """Calculate statistics for the website."""
    total = len(papers)
    with_abstract = sum(1 for p in papers if p["abstract"])
    with_doi = sum(1 for p in papers if p["doi"])
    total_citations = sum(p["citations"] for p in papers)

    # Year distribution
    years = {}
    for p in papers:
        if p["year"]:
            years[p["year"]] = years.get(p["year"], 0) + 1

    return {
        "total": total,
        "with_abstract": with_abstract,
        "with_doi": with_doi,
        "total_citations": total_citations,
        "years": dict(sorted(years.items())),
    }


def _generate_html(title: str, papers: list, stats: dict) -> str:
    """Generate the HTML content."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="stats">
                <div class="stat">
                    <span class="stat-value">{stats["total"]}</span>
                    <span class="stat-label">Total Papers</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{stats["with_doi"]}</span>
                    <span class="stat-label">With DOI</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{stats["with_abstract"]}</span>
                    <span class="stat-label">With Abstract</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{stats["total_citations"]:,}</span>
                    <span class="stat-label">Total Citations</span>
                </div>
            </div>
        </header>

        <div class="controls">
            <button id="download-csv">Download CSV</button>
            <button id="download-json">Download JSON</button>
        </div>

        <div id="papers-table"></div>
    </div>

    <script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
    <script src="js/papers.js"></script>
    <script>
        const table = new Tabulator("#papers-table", {{
            data: papersData,
            layout: "fitColumns",
            pagination: true,
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            initialSort: [{{column: "citations", dir: "desc"}}],
            columns: [
                {{title: "Title", field: "title", headerFilter: "input", formatter: function(cell) {{
                    const data = cell.getRow().getData();
                    if (data.doi_url) {{
                        return '<a href="' + data.doi_url + '" target="_blank">' + cell.getValue() + '</a>';
                    }}
                    return cell.getValue();
                }}, widthGrow: 3}},
                {{title: "Year", field: "year", headerFilter: "input", sorter: "number", width: 80}},
                {{title: "Citations", field: "citations", sorter: "number", width: 100, headerFilter: "number", headerFilterFunc: ">="}},
                {{title: "Publication", field: "publication", headerFilter: "input", widthGrow: 1}},
                {{title: "PDF", field: "pdf_url", formatter: function(cell) {{
                    if (cell.getValue()) {{
                        return '<a href="' + cell.getValue() + '" target="_blank">PDF</a>';
                    }}
                    return '';
                }}, width: 60}},
            ],
        }});

        document.getElementById("download-csv").addEventListener("click", function() {{
            table.download("csv", "papers.csv");
        }});

        document.getElementById("download-json").addEventListener("click", function() {{
            table.download("json", "papers.json");
        }});
    </script>
</body>
</html>
'''


def _generate_js_data(papers: list) -> str:
    """Generate the JavaScript data file."""
    return f"const papersData = {json.dumps(papers, ensure_ascii=False, indent=2)};"


def _generate_css() -> str:
    """Generate the CSS content."""
    return '''
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f6f8fa;
    margin: 0;
    padding: 20px;
    color: #24292e;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

header {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

h1 {
    margin: 0 0 20px 0;
    color: #2c5aa0;
}

.stats {
    display: flex;
    gap: 30px;
    flex-wrap: wrap;
}

.stat {
    display: flex;
    flex-direction: column;
}

.stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #2c5aa0;
}

.stat-label {
    font-size: 14px;
    color: #666;
}

.controls {
    margin-bottom: 15px;
    display: flex;
    gap: 10px;
}

.controls button {
    background: #2c5aa0;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

.controls button:hover {
    background: #1a4480;
}

#papers-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tabulator-row a {
    color: #0366d6;
    text-decoration: none;
}

.tabulator-row a:hover {
    text-decoration: underline;
}
'''
