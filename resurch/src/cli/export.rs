//! Export subcommand implementation

use crate::cli::args::ExportArgs;
use crate::db::{Database, PaperRepository};
use crate::models::Paper;
use anyhow::{Context, Result};
use std::fs::File;
use std::io::{BufWriter, Write};

/// Run the export subcommand
pub async fn run(args: ExportArgs) -> Result<()> {
    let db = Database::open_default()?;
    let paper_repo = PaperRepository::new(&db);

    // Get all papers
    let papers = paper_repo.list(None, None)?;

    // Filter papers
    let filtered: Vec<Paper> = papers
        .into_iter()
        .filter(|p| {
            if let Some(min_cites) = args.min_citations {
                if p.citations < min_cites {
                    return false;
                }
            }
            if args.with_abstract && p.abstract_text.is_none() {
                return false;
            }
            if args.with_doi && p.doi.is_none() {
                return false;
            }
            true
        })
        .collect();

    eprintln!("Exporting {} papers...", filtered.len());

    // Create output writer
    let writer: Box<dyn Write> = if let Some(ref path) = args.file {
        Box::new(BufWriter::new(
            File::create(path).context("Failed to create output file")?,
        ))
    } else {
        Box::new(std::io::stdout())
    };

    match args.output.as_str() {
        "csv" => export_csv(writer, &filtered)?,
        _ => export_json(writer, &filtered)?,
    }

    if let Some(ref path) = args.file {
        eprintln!("Exported to {:?}", path);
    }

    Ok(())
}

/// Export papers as JSON
fn export_json<W: Write>(mut writer: W, papers: &[Paper]) -> Result<()> {
    // Build output structure matching the existing format
    let count_abstract = papers.iter().filter(|p| p.abstract_text.is_some()).count();
    let count_doi = papers.iter().filter(|p| p.doi.is_some()).count();
    let count_2 = papers.iter().filter(|p| p.citations >= 2).count();

    let output = serde_json::json!({
        "count": papers.len(),
        "count_2": count_2,
        "count_abstract": count_abstract,
        "count_doi": count_doi,
        "results": papers
    });

    serde_json::to_writer_pretty(&mut writer, &output)?;
    writeln!(writer)?;
    Ok(())
}

/// Export papers as CSV
fn export_csv<W: Write>(writer: W, papers: &[Paper]) -> Result<()> {
    let mut csv_writer = csv::Writer::from_writer(writer);

    // Write header
    csv_writer.write_record([
        "id",
        "doi",
        "title",
        "citations",
        "year",
        "publication",
        "abstract",
        "publisher_url",
        "doi_url",
        "source",
        "authors",
        "publisher",
    ])?;

    // Write rows
    for paper in papers {
        csv_writer.write_record([
            paper.id.map(|i| i.to_string()).unwrap_or_default(),
            paper.doi.clone().unwrap_or_default(),
            paper.title.clone(),
            paper.citations.to_string(),
            paper.year.map(|y| y.to_string()).unwrap_or_default(),
            paper.publication.clone().unwrap_or_default(),
            paper.abstract_text.clone().unwrap_or_default(),
            paper.publisher_url.clone().unwrap_or_default(),
            paper.doi_url.clone().unwrap_or_default(),
            paper.source_repository.clone().unwrap_or_default(),
            paper.authors.join("; "),
            paper.publisher.clone().unwrap_or_default(),
        ])?;
    }

    csv_writer.flush()?;
    Ok(())
}
