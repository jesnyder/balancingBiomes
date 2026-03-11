//! Static website generation

mod data;
mod templates;

use crate::models::Paper;
use anyhow::{Context, Result};
use std::fs;
use std::path::PathBuf;

/// Website generation configuration
pub struct WebsiteConfig {
    pub title: String,
    pub output_dir: PathBuf,
    pub min_citations: i32,
}

/// Generate a static website
pub fn generate_website(papers: &[Paper], config: &WebsiteConfig) -> Result<()> {
    // Create output directories
    fs::create_dir_all(&config.output_dir).context("Failed to create output directory")?;
    fs::create_dir_all(config.output_dir.join("js")).context("Failed to create js directory")?;
    fs::create_dir_all(config.output_dir.join("data"))
        .context("Failed to create data directory")?;

    // Filter papers for display
    let display_papers: Vec<&Paper> = papers
        .iter()
        .filter(|p| p.citations >= config.min_citations)
        .collect();

    // Generate JSON data files
    data::generate_papers_json(&display_papers, &config.output_dir.join("data/papers.json"))?;
    data::generate_stats_json(papers, &config.output_dir.join("data/stats.json"))?;

    // Generate HTML and JS files
    templates::generate_index_html(config, &config.output_dir.join("index.html"))?;
    templates::generate_table_js(&config.output_dir.join("js/table.js"))?;
    templates::generate_charts_js(&config.output_dir.join("js/charts.js"))?;

    Ok(())
}

// Re-export for library users
#[allow(unused_imports)]
pub use data::{generate_papers_json, generate_stats_json};
#[allow(unused_imports)]
pub use templates::{generate_charts_js, generate_index_html, generate_table_js};
