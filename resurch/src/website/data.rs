//! Data generation for website

use crate::models::Paper;
use anyhow::{Context, Result};
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::path::Path;

/// Generate papers JSON for Tabulator table
pub fn generate_papers_json(papers: &[&Paper], output: &Path) -> Result<()> {
    let file = File::create(output).context("Failed to create papers JSON file")?;
    let writer = BufWriter::new(file);

    serde_json::to_writer_pretty(writer, papers)?;
    Ok(())
}

/// Generate statistics JSON for charts
pub fn generate_stats_json(papers: &[Paper], output: &Path) -> Result<()> {
    let file = File::create(output).context("Failed to create stats JSON file")?;
    let writer = BufWriter::new(file);

    // Count by year
    let mut by_year: HashMap<u16, i32> = HashMap::new();
    for paper in papers {
        if let Some(year) = paper.year {
            *by_year.entry(year).or_insert(0) += 1;
        }
    }
    let mut years: Vec<(u16, i32)> = by_year.into_iter().collect();
    years.sort_by_key(|(y, _)| *y);

    // Count by source
    let mut by_source: HashMap<String, i32> = HashMap::new();
    for paper in papers {
        let source = paper
            .source_repository
            .clone()
            .unwrap_or_else(|| "unknown".to_string());
        *by_source.entry(source).or_insert(0) += 1;
    }

    // Citation distribution
    let mut citation_buckets: HashMap<String, i32> = HashMap::new();
    for paper in papers {
        let bucket = match paper.citations {
            0 => "0",
            1..=5 => "1-5",
            6..=20 => "6-20",
            21..=100 => "21-100",
            _ => "100+",
        };
        *citation_buckets.entry(bucket.to_string()).or_insert(0) += 1;
    }

    let stats = serde_json::json!({
        "total_papers": papers.len(),
        "papers_with_doi": papers.iter().filter(|p| p.doi.is_some()).count(),
        "papers_with_abstract": papers.iter().filter(|p| p.abstract_text.is_some()).count(),
        "papers_with_2_citations": papers.iter().filter(|p| p.citations >= 2).count(),
        "by_year": years,
        "by_source": by_source,
        "citation_distribution": citation_buckets,
    });

    serde_json::to_writer_pretty(writer, &stats)?;
    Ok(())
}
