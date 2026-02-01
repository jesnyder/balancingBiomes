//! Database schema and connection management

use anyhow::{Context, Result};
use directories::ProjectDirs;
use rusqlite::Connection;
use std::path::PathBuf;

/// Database wrapper providing connection and initialization
pub struct Database {
    conn: Connection,
}

impl Database {
    /// Open or create the database at the default location
    pub fn open_default() -> Result<Self> {
        let path = Self::default_path()?;
        Self::open(&path)
    }

    /// Open or create the database at a specific path
    pub fn open(path: &PathBuf) -> Result<Self> {
        // Ensure parent directory exists
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .with_context(|| format!("Failed to create database directory: {:?}", parent))?;
        }

        let conn = Connection::open(path)
            .with_context(|| format!("Failed to open database at {:?}", path))?;

        let db = Self { conn };
        db.initialize()?;
        Ok(db)
    }

    /// Open an in-memory database (for testing)
    pub fn open_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        let db = Self { conn };
        db.initialize()?;
        Ok(db)
    }

    /// Get the default database path (XDG compliant)
    pub fn default_path() -> Result<PathBuf> {
        let proj_dirs = ProjectDirs::from("com", "resurch", "resurch")
            .context("Could not determine project directories")?;

        let data_dir = proj_dirs.data_dir();
        Ok(data_dir.join("resurch.db"))
    }

    /// Get a reference to the connection
    pub fn conn(&self) -> &Connection {
        &self.conn
    }

    /// Get a mutable reference to the connection
    pub fn conn_mut(&mut self) -> &mut Connection {
        &mut self.conn
    }

    /// Initialize the database schema
    fn initialize(&self) -> Result<()> {
        self.conn.execute_batch(
            r#"
            -- Core paper storage
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doi TEXT UNIQUE,
                title TEXT NOT NULL,
                title_normalized TEXT NOT NULL,
                citations INTEGER DEFAULT 0,
                year INTEGER,
                publication TEXT,
                abstract_text TEXT,
                snippet TEXT,
                publisher_url TEXT,
                doi_url TEXT,
                source_repository TEXT,
                raw_json TEXT,
                authors TEXT,
                publisher TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Index for deduplication
            CREATE INDEX IF NOT EXISTS idx_papers_title_normalized ON papers(title_normalized);
            CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
            CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
            CREATE INDEX IF NOT EXISTS idx_papers_citations ON papers(citations);

            -- Search sessions for resumability
            CREATE TABLE IF NOT EXISTS search_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                repository TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                max_results INTEGER,
                current_offset INTEGER DEFAULT 0,
                results_fetched INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            -- Enrichment queue
            CREATE TABLE IF NOT EXISTS enrichment_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
                status TEXT DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                last_error TEXT,
                UNIQUE(paper_id)
            );

            -- Query history
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                result_count INTEGER,
                executed_at TEXT DEFAULT (datetime('now'))
            );
            "#,
        )?;

        Ok(())
    }

    /// Get database statistics
    pub fn stats(&self) -> Result<DatabaseStats> {
        let total_papers: i64 = self
            .conn
            .query_row("SELECT COUNT(*) FROM papers", [], |row| row.get(0))?;

        let papers_with_doi: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM papers WHERE doi IS NOT NULL AND doi != ''",
            [],
            |row| row.get(0),
        )?;

        let papers_with_abstract: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM papers WHERE abstract_text IS NOT NULL AND abstract_text != ''",
            [],
            |row| row.get(0),
        )?;

        let papers_with_citations: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM papers WHERE citations >= 2",
            [],
            |row| row.get(0),
        )?;

        let pending_enrichment: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM enrichment_queue WHERE status = 'pending'",
            [],
            |row| row.get(0),
        )?;

        let active_sessions: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM search_sessions WHERE status IN ('pending', 'in_progress')",
            [],
            |row| row.get(0),
        )?;

        Ok(DatabaseStats {
            total_papers,
            papers_with_doi,
            papers_with_abstract,
            papers_with_citations,
            pending_enrichment,
            active_sessions,
        })
    }
}

/// Database statistics
#[derive(Debug)]
pub struct DatabaseStats {
    pub total_papers: i64,
    pub papers_with_doi: i64,
    pub papers_with_abstract: i64,
    pub papers_with_citations: i64,
    pub pending_enrichment: i64,
    pub active_sessions: i64,
}

impl std::fmt::Display for DatabaseStats {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        writeln!(f, "Database Statistics")?;
        writeln!(f, "===================")?;
        writeln!(f, "Total papers:         {}", self.total_papers)?;
        writeln!(f, "Papers with DOI:      {}", self.papers_with_doi)?;
        writeln!(f, "Papers with abstract: {}", self.papers_with_abstract)?;
        writeln!(f, "Papers with 2+ cites: {}", self.papers_with_citations)?;
        writeln!(f, "Pending enrichment:   {}", self.pending_enrichment)?;
        writeln!(f, "Active sessions:      {}", self.active_sessions)?;
        Ok(())
    }
}
