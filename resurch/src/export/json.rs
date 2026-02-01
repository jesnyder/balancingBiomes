//! JSON export

use crate::models::Paper;
use anyhow::Result;
use std::io::Write;

/// Export papers to JSON format matching the existing standardized format
pub fn export_json<W: Write>(mut writer: W, papers: &[Paper]) -> Result<()> {
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
