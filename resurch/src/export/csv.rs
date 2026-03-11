//! CSV export

use crate::models::Paper;
use anyhow::Result;
use std::io::Write;

/// Export papers to CSV format
pub fn export_csv<W: Write>(writer: W, papers: &[Paper]) -> Result<()> {
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
