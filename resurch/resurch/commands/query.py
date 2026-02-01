"""Query command implementation."""

import re
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import text

from ..database import session_scope, init_db

console = Console()


def query_cmd(
    sql: str = typer.Argument(..., help="SQL query to execute."),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table, json, csv"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit number of results"
    ),
):
    """
    Query the paper database with SQL.

    Supports a "read-my-mind" forgiving SQL mode for simple queries.

    Examples:
        resurch query "SELECT title, citations FROM papers ORDER BY citations DESC LIMIT 10"
        resurch query "papers where citations > 100" --format json
        resurch query "title, year from papers" --limit 5
    """
    init_db()

    # Parse and potentially fix the SQL
    sql = _parse_forgiving_sql(sql)

    # Add limit if specified and not already in query
    if limit and "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {limit}"

    try:
        with session_scope() as session:
            result = session.execute(text(sql))
            columns = result.keys()
            rows = result.fetchall()

        if not rows:
            console.print("[yellow]No results found.[/yellow]")
            return

        if format == "table":
            _print_table(columns, rows)
        elif format == "json":
            _print_json(columns, rows)
        elif format == "csv":
            _print_csv(columns, rows)
        else:
            console.print(f"[red]Unknown format: {format}[/red]")

    except Exception as e:
        console.print(f"[red]Query error:[/red] {e}")
        console.print(f"[dim]SQL: {sql}[/dim]")


def _parse_forgiving_sql(sql: str) -> str:
    """
    Parse a forgiving SQL syntax and convert to valid SQL.

    Supports:
    - "papers" -> "SELECT * FROM papers"
    - "papers where citations > 100" -> "SELECT * FROM papers WHERE citations > 100"
    - "title, year from papers" -> "SELECT title, year FROM papers"
    - Full SQL passthrough
    """
    sql = sql.strip()

    # If it starts with SELECT, it's already SQL
    if sql.upper().startswith("SELECT"):
        return sql

    # Check for "from" keyword
    from_match = re.search(r'\bfrom\b', sql, re.IGNORECASE)
    if from_match:
        # Format: "columns from table [where ...]"
        columns = sql[:from_match.start()].strip()
        rest = sql[from_match.end():].strip()
        return f"SELECT {columns} FROM {rest}"

    # Check for table name only or "table where condition"
    where_match = re.search(r'\bwhere\b', sql, re.IGNORECASE)
    if where_match:
        # Format: "table where condition"
        table = sql[:where_match.start()].strip()
        condition = sql[where_match.end():].strip()
        return f"SELECT * FROM {table} WHERE {condition}"

    # Check if it's just a table name
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', sql):
        return f"SELECT * FROM {sql}"

    # Default: treat as full SQL
    return sql


def _print_table(columns, rows):
    """Print results as a Rich table."""
    table = Table(show_header=True, header_style="bold magenta")

    for col in columns:
        table.add_column(str(col))

    for row in rows:
        table.add_row(*[_format_cell(cell) for cell in row])

    console.print(table)
    console.print(f"\n[dim]{len(rows)} rows[/dim]")


def _print_json(columns, rows):
    """Print results as JSON."""
    import json

    data = []
    for row in rows:
        data.append(dict(zip(columns, [_serialize_cell(cell) for cell in row])))

    console.print(json.dumps(data, indent=2, ensure_ascii=False))


def _print_csv(columns, rows):
    """Print results as CSV."""
    import csv
    import sys

    writer = csv.writer(sys.stdout)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_serialize_cell(cell) for cell in row])


def _format_cell(value) -> str:
    """Format a cell value for table display."""
    if value is None:
        return ""
    if isinstance(value, str) and len(value) > 80:
        return value[:77] + "..."
    return str(value)


def _serialize_cell(value):
    """Serialize a cell value for JSON/CSV."""
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return value
