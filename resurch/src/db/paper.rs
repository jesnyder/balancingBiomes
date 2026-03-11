//! Paper CRUD operations

use crate::models::Paper;
use anyhow::{Context, Result};
use rusqlite::{params, OptionalExtension};

use super::Database;

/// Repository for paper CRUD operations
pub struct PaperRepository<'a> {
    db: &'a Database,
}

impl<'a> PaperRepository<'a> {
    pub fn new(db: &'a Database) -> Self {
        Self { db }
    }

    /// Insert a new paper, handling deduplication
    /// Returns the paper ID (existing or new)
    pub fn insert_or_update(&self, paper: &Paper) -> Result<i64> {
        let conn = self.db.conn();
        let title_normalized = paper
            .title_normalized
            .clone()
            .unwrap_or_else(|| Paper::normalize_title(&paper.title));

        // First, try to find by DOI if present
        if let Some(ref doi) = paper.doi {
            if !doi.is_empty() {
                if let Some(id) = self.find_by_doi(doi)? {
                    // Update existing record
                    self.update(id, paper)?;
                    return Ok(id);
                }
            }
        }

        // Next, try to find by normalized title
        if let Some(id) = self.find_by_normalized_title(&title_normalized)? {
            // Update existing record
            self.update(id, paper)?;
            return Ok(id);
        }

        // Insert new record
        let authors_json = if paper.authors.is_empty() {
            None
        } else {
            Some(serde_json::to_string(&paper.authors)?)
        };

        conn.execute(
            r#"
            INSERT INTO papers (
                doi, title, title_normalized, citations, year, publication,
                abstract_text, snippet, publisher_url, doi_url, source_repository,
                raw_json, authors, publisher
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14)
            "#,
            params![
                paper.doi,
                paper.title,
                title_normalized,
                paper.citations,
                paper.year.map(|y| y as i32),
                paper.publication,
                paper.abstract_text,
                paper.snippet,
                paper.publisher_url,
                paper.doi_url,
                paper.source_repository,
                paper.raw_json,
                authors_json,
                paper.publisher,
            ],
        )?;

        Ok(conn.last_insert_rowid())
    }

    /// Update an existing paper
    pub fn update(&self, id: i64, paper: &Paper) -> Result<()> {
        let conn = self.db.conn();
        let title_normalized = paper
            .title_normalized
            .clone()
            .unwrap_or_else(|| Paper::normalize_title(&paper.title));

        let authors_json = if paper.authors.is_empty() {
            None
        } else {
            Some(serde_json::to_string(&paper.authors)?)
        };

        conn.execute(
            r#"
            UPDATE papers SET
                doi = COALESCE(?1, doi),
                title = ?2,
                title_normalized = ?3,
                citations = MAX(citations, ?4),
                year = COALESCE(?5, year),
                publication = COALESCE(?6, publication),
                abstract_text = COALESCE(?7, abstract_text),
                snippet = COALESCE(?8, snippet),
                publisher_url = COALESCE(?9, publisher_url),
                doi_url = COALESCE(?10, doi_url),
                source_repository = COALESCE(?11, source_repository),
                raw_json = COALESCE(?12, raw_json),
                authors = COALESCE(?13, authors),
                publisher = COALESCE(?14, publisher),
                updated_at = datetime('now')
            WHERE id = ?15
            "#,
            params![
                paper.doi,
                paper.title,
                title_normalized,
                paper.citations,
                paper.year.map(|y| y as i32),
                paper.publication,
                paper.abstract_text,
                paper.snippet,
                paper.publisher_url,
                paper.doi_url,
                paper.source_repository,
                paper.raw_json,
                authors_json,
                paper.publisher,
                id,
            ],
        )?;

        Ok(())
    }

    /// Find a paper by DOI
    pub fn find_by_doi(&self, doi: &str) -> Result<Option<i64>> {
        let conn = self.db.conn();
        conn.query_row("SELECT id FROM papers WHERE doi = ?1", [doi], |row| {
            row.get(0)
        })
        .optional()
        .context("Failed to query paper by DOI")
    }

    /// Find a paper by normalized title
    pub fn find_by_normalized_title(&self, title_normalized: &str) -> Result<Option<i64>> {
        let conn = self.db.conn();
        conn.query_row(
            "SELECT id FROM papers WHERE title_normalized = ?1",
            [title_normalized],
            |row| row.get(0),
        )
        .optional()
        .context("Failed to query paper by normalized title")
    }

    /// Get a paper by ID
    pub fn get(&self, id: i64) -> Result<Option<Paper>> {
        let conn = self.db.conn();
        conn.query_row(
            r#"
            SELECT id, doi, title, title_normalized, citations, year, publication,
                   abstract_text, snippet, publisher_url, doi_url, source_repository,
                   raw_json, authors, publisher, created_at, updated_at
            FROM papers WHERE id = ?1
            "#,
            [id],
            |row| {
                Ok(Paper {
                    id: Some(row.get(0)?),
                    doi: row.get(1)?,
                    title: row.get(2)?,
                    title_normalized: row.get(3)?,
                    citations: row.get(4)?,
                    year: row.get::<_, Option<i32>>(5)?.map(|y| y as u16),
                    publication: row.get(6)?,
                    abstract_text: row.get(7)?,
                    snippet: row.get(8)?,
                    publisher_url: row.get(9)?,
                    doi_url: row.get(10)?,
                    source_repository: row.get(11)?,
                    raw_json: row.get(12)?,
                    authors: row
                        .get::<_, Option<String>>(13)?
                        .and_then(|s| serde_json::from_str(&s).ok())
                        .unwrap_or_default(),
                    publisher: row.get(14)?,
                    created_at: row.get(15)?,
                    updated_at: row.get(16)?,
                })
            },
        )
        .optional()
        .context("Failed to get paper by ID")
    }

    /// Get all papers, optionally filtered and sorted
    pub fn list(&self, limit: Option<u32>, offset: Option<u32>) -> Result<Vec<Paper>> {
        let conn = self.db.conn();
        let limit = limit.unwrap_or(1000);
        let offset = offset.unwrap_or(0);

        let mut stmt = conn.prepare(
            r#"
            SELECT id, doi, title, title_normalized, citations, year, publication,
                   abstract_text, snippet, publisher_url, doi_url, source_repository,
                   raw_json, authors, publisher, created_at, updated_at
            FROM papers
            ORDER BY citations DESC, year DESC
            LIMIT ?1 OFFSET ?2
            "#,
        )?;

        let papers = stmt
            .query_map([limit, offset], |row| {
                Ok(Paper {
                    id: Some(row.get(0)?),
                    doi: row.get(1)?,
                    title: row.get(2)?,
                    title_normalized: row.get(3)?,
                    citations: row.get(4)?,
                    year: row.get::<_, Option<i32>>(5)?.map(|y| y as u16),
                    publication: row.get(6)?,
                    abstract_text: row.get(7)?,
                    snippet: row.get(8)?,
                    publisher_url: row.get(9)?,
                    doi_url: row.get(10)?,
                    source_repository: row.get(11)?,
                    raw_json: row.get(12)?,
                    authors: row
                        .get::<_, Option<String>>(13)?
                        .and_then(|s| serde_json::from_str(&s).ok())
                        .unwrap_or_default(),
                    publisher: row.get(14)?,
                    created_at: row.get(15)?,
                    updated_at: row.get(16)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(papers)
    }

    /// Count total papers
    pub fn count(&self) -> Result<i64> {
        let conn = self.db.conn();
        conn.query_row("SELECT COUNT(*) FROM papers", [], |row| row.get(0))
            .context("Failed to count papers")
    }

    /// Get papers missing DOI or abstract for enrichment
    pub fn get_papers_needing_enrichment(&self, limit: u32) -> Result<Vec<Paper>> {
        let conn = self.db.conn();
        let mut stmt = conn.prepare(
            r#"
            SELECT id, doi, title, title_normalized, citations, year, publication,
                   abstract_text, snippet, publisher_url, doi_url, source_repository,
                   raw_json, authors, publisher, created_at, updated_at
            FROM papers
            WHERE (doi IS NULL OR doi = '') OR (abstract_text IS NULL OR abstract_text = '')
            ORDER BY citations DESC
            LIMIT ?1
            "#,
        )?;

        let papers = stmt
            .query_map([limit], |row| {
                Ok(Paper {
                    id: Some(row.get(0)?),
                    doi: row.get(1)?,
                    title: row.get(2)?,
                    title_normalized: row.get(3)?,
                    citations: row.get(4)?,
                    year: row.get::<_, Option<i32>>(5)?.map(|y| y as u16),
                    publication: row.get(6)?,
                    abstract_text: row.get(7)?,
                    snippet: row.get(8)?,
                    publisher_url: row.get(9)?,
                    doi_url: row.get(10)?,
                    source_repository: row.get(11)?,
                    raw_json: row.get(12)?,
                    authors: row
                        .get::<_, Option<String>>(13)?
                        .and_then(|s| serde_json::from_str(&s).ok())
                        .unwrap_or_default(),
                    publisher: row.get(14)?,
                    created_at: row.get(15)?,
                    updated_at: row.get(16)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(papers)
    }
}
