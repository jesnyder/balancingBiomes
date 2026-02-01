//! CLI argument definitions using clap

use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "resurch")]
#[command(author, version, about = "Academic paper search CLI tool")]
#[command(propagate_version = true)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,

    /// Database path (default: ~/.local/share/resurch/resurch.db)
    #[arg(long, short = 'd', global = true)]
    pub database: Option<PathBuf>,
}

#[derive(Subcommand)]
pub enum Command {
    /// Search for papers in academic repositories
    Search(SearchArgs),

    /// Enrich papers with missing metadata (DOI, abstract)
    Enrich(EnrichArgs),

    /// Execute SQL queries on the database
    Query(QueryArgs),

    /// Export papers to CSV or JSON
    Export(ExportArgs),

    /// Generate a static website with search results
    Website(WebsiteArgs),

    /// Show database statistics
    Stats(StatsArgs),
}

#[derive(Parser)]
pub struct SearchArgs {
    /// Search query (e.g., "halophyte AND halophile")
    #[arg(required_unless_present_any = ["list", "resume"])]
    pub query: Option<String>,

    /// Repository to search: crossref, openalex, semantic_scholar, google_scholar
    #[arg(long, short = 'w', default_value = "crossref")]
    pub r#where: String,

    /// Maximum number of results to fetch
    #[arg(long, short = 'm', default_value = "100")]
    pub max_results: u32,

    /// List active/resumable search sessions
    #[arg(long, short = 'l')]
    pub list: bool,

    /// Resume a specific search session by ID
    #[arg(long, short = 'r')]
    pub resume: Option<i64>,
}

#[derive(Parser)]
pub struct EnrichArgs {
    /// Maximum number of papers to enrich
    #[arg(long, short = 'm', default_value = "50")]
    pub max: u32,

    /// Queue all papers needing enrichment
    #[arg(long, short = 'q')]
    pub queue: bool,

    /// Show enrichment queue status
    #[arg(long, short = 's')]
    pub status: bool,
}

#[derive(Parser)]
pub struct QueryArgs {
    /// SQL query to execute
    pub sql: String,

    /// Output format: table, json, csv
    #[arg(long, short = 'o', default_value = "table")]
    pub output: String,
}

#[derive(Parser)]
pub struct ExportArgs {
    /// Output format: csv, json
    #[arg(long, short = 'o', default_value = "json")]
    pub output: String,

    /// Output file (default: stdout)
    #[arg(long, short = 'f')]
    pub file: Option<PathBuf>,

    /// Minimum citations filter
    #[arg(long)]
    pub min_citations: Option<i32>,

    /// Only include papers with abstracts
    #[arg(long)]
    pub with_abstract: bool,

    /// Only include papers with DOI
    #[arg(long)]
    pub with_doi: bool,
}

#[derive(Parser)]
pub struct WebsiteArgs {
    /// Output directory for the static website
    #[arg(long, short = 'o', default_value = "./site")]
    pub output: PathBuf,

    /// Site title
    #[arg(long, default_value = "Research Papers")]
    pub title: String,

    /// Minimum citations to include in tables
    #[arg(long, default_value = "2")]
    pub min_citations: i32,
}

#[derive(Parser)]
pub struct StatsArgs {
    /// Show detailed statistics
    #[arg(long, short = 'v')]
    pub verbose: bool,
}
