//! Enrichment queue for papers needing additional metadata

use anyhow::{Context, Result};
use rusqlite::{params, OptionalExtension};

use super::Database;

/// Enrichment queue entry
#[derive(Debug, Clone)]
pub struct EnrichmentEntry {
    pub id: i64,
    pub paper_id: i64,
    pub status: String,
    pub attempts: i32,
    pub last_error: Option<String>,
}

/// Queue for papers needing enrichment
pub struct EnrichmentQueue<'a> {
    db: &'a Database,
}

impl<'a> EnrichmentQueue<'a> {
    pub fn new(db: &'a Database) -> Self {
        Self { db }
    }

    /// Add a paper to the enrichment queue
    pub fn enqueue(&self, paper_id: i64) -> Result<()> {
        let conn = self.db.conn();
        conn.execute(
            "INSERT OR IGNORE INTO enrichment_queue (paper_id, status, attempts) VALUES (?1, 'pending', 0)",
            [paper_id],
        )?;
        Ok(())
    }

    /// Get the next paper to enrich
    pub fn dequeue(&self) -> Result<Option<EnrichmentEntry>> {
        let conn = self.db.conn();
        conn.query_row(
            r#"
            SELECT id, paper_id, status, attempts, last_error
            FROM enrichment_queue
            WHERE status = 'pending' AND attempts < 3
            ORDER BY id ASC
            LIMIT 1
            "#,
            [],
            |row| {
                Ok(EnrichmentEntry {
                    id: row.get(0)?,
                    paper_id: row.get(1)?,
                    status: row.get(2)?,
                    attempts: row.get(3)?,
                    last_error: row.get(4)?,
                })
            },
        )
        .optional()
        .context("Failed to dequeue enrichment entry")
    }

    /// Mark an entry as completed
    pub fn mark_completed(&self, id: i64) -> Result<()> {
        let conn = self.db.conn();
        conn.execute(
            "UPDATE enrichment_queue SET status = 'completed' WHERE id = ?1",
            [id],
        )?;
        Ok(())
    }

    /// Mark an entry as failed and increment attempts
    pub fn mark_failed(&self, id: i64, error: &str) -> Result<()> {
        let conn = self.db.conn();
        conn.execute(
            r#"
            UPDATE enrichment_queue
            SET status = CASE WHEN attempts >= 2 THEN 'failed' ELSE 'pending' END,
                attempts = attempts + 1,
                last_error = ?1
            WHERE id = ?2
            "#,
            params![error, id],
        )?;
        Ok(())
    }

    /// Get count of pending entries
    pub fn pending_count(&self) -> Result<i64> {
        let conn = self.db.conn();
        conn.query_row(
            "SELECT COUNT(*) FROM enrichment_queue WHERE status = 'pending'",
            [],
            |row| row.get(0),
        )
        .context("Failed to count pending enrichment entries")
    }

    /// Queue all papers missing DOI or abstract
    pub fn queue_papers_needing_enrichment(&self) -> Result<i64> {
        let conn = self.db.conn();
        conn.execute(
            r#"
            INSERT OR IGNORE INTO enrichment_queue (paper_id, status, attempts)
            SELECT id, 'pending', 0
            FROM papers
            WHERE (doi IS NULL OR doi = '') OR (abstract_text IS NULL OR abstract_text = '')
            "#,
            [],
        )?;

        self.pending_count()
    }
}
