//! CLI module

pub mod args;
mod enrich;
mod export;
mod query;
mod search;
mod stats;
mod website;

use anyhow::Result;
pub use args::Cli;

/// Run the CLI
pub async fn run(cli: Cli) -> Result<()> {
    match cli.command {
        args::Command::Search(args) => search::run(args).await,
        args::Command::Enrich(args) => enrich::run(args).await,
        args::Command::Query(args) => query::run(args).await,
        args::Command::Export(args) => export::run(args).await,
        args::Command::Website(args) => website::run(args).await,
        args::Command::Stats(args) => stats::run(args).await,
    }
}
