//! Website subcommand implementation

use crate::cli::args::WebsiteArgs;
use crate::db::{Database, PaperRepository};
use crate::website::{generate_website, WebsiteConfig};
use anyhow::Result;

/// Run the website subcommand
pub async fn run(args: WebsiteArgs) -> Result<()> {
    let db = Database::open_default()?;
    let paper_repo = PaperRepository::new(&db);

    // Get all papers
    let papers = paper_repo.list(None, None)?;

    let config = WebsiteConfig {
        title: args.title,
        output_dir: args.output,
        min_citations: args.min_citations,
    };

    generate_website(&papers, &config)?;

    println!(
        "Website generated at {:?}",
        config.output_dir.canonicalize()?
    );
    println!("Run: python3 -m http.server -d {:?}", config.output_dir);

    Ok(())
}
