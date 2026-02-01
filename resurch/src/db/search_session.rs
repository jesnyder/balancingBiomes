//! Search session tracking for resumability

use anyhow::{Context, Result};
use rusqlite::{params, OptionalExtension};
use serde::{Deserialize, Serialize};

use super::Database;

/// Status of a search session
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SessionStatus {
    Pending,
    InProgress,
    Completed,
    Interrupted,
}

impl std::fmt::Display for SessionStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SessionStatus::Pending => write!(f, "pending"),
            SessionStatus::InProgress => write!(f, "in_progress"),
            SessionStatus::Completed => write!(f, "completed"),
            SessionStatus::Interrupted => write!(f, "interrupted"),
        }
    }
}

impl std::str::FromStr for SessionStatus {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self> {
        match s {
            "pending" => Ok(SessionStatus::Pending),
            "in_progress" => Ok(SessionStatus::InProgress),
            "completed" => Ok(SessionStatus::Completed),
            "interrupted" => Ok(SessionStatus::Interrupted),
            _ => anyhow::bail!("Unknown session status: {}", s),
        }
    }
}

/// A search session for tracking progress
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchSession {
    pub id: Option<i64>,
    pub query: String,
    pub repository: String,
    pub status: SessionStatus,
    pub max_results: Option<i32>,
    pub current_offset: i32,
    pub results_fetched: i32,
    pub created_at: Option<String>,
}

impl SearchSession {
    pub fn new(query: impl Into<String>, repository: impl Into<String>) -> Self {
        Self {
            id: None,
            query: query.into(),
            repository: repository.into(),
            status: SessionStatus::Pending,
            max_results: None,
            current_offset: 0,
            results_fetched: 0,
            created_at: None,
        }
    }

    pub fn with_max_results(mut self, max: i32) -> Self {
        self.max_results = Some(max);
        self
    }
}

/// Repository for search session operations
pub struct SearchSessionRepository<'a> {
    db: &'a Database,
}

impl<'a> SearchSessionRepository<'a> {
    pub fn new(db: &'a Database) -> Self {
        Self { db }
    }

    /// Create a new search session
    pub fn create(&self, session: &SearchSession) -> Result<i64> {
        let conn = self.db.conn();
        conn.execute(
            r#"
            INSERT INTO search_sessions (query, repository, status, max_results, current_offset, results_fetched)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6)
            "#,
            params![
                session.query,
                session.repository,
                session.status.to_string(),
                session.max_results,
                session.current_offset,
                session.results_fetched,
            ],
        )?;

        Ok(conn.last_insert_rowid())
    }

    /// Get a session by ID
    pub fn get(&self, id: i64) -> Result<Option<SearchSession>> {
        let conn = self.db.conn();
        conn.query_row(
            r#"
            SELECT id, query, repository, status, max_results, current_offset, results_fetched, created_at
            FROM search_sessions WHERE id = ?1
            "#,
            [id],
            |row| {
                let status_str: String = row.get(3)?;
                Ok(SearchSession {
                    id: Some(row.get(0)?),
                    query: row.get(1)?,
                    repository: row.get(2)?,
                    status: status_str.parse().unwrap_or(SessionStatus::Pending),
                    max_results: row.get(4)?,
                    current_offset: row.get(5)?,
                    results_fetched: row.get(6)?,
                    created_at: row.get(7)?,
                })
            },
        )
        .optional()
        .context("Failed to get search session")
    }

    /// Update session progress
    pub fn update_progress(&self, id: i64, offset: i32, fetched: i32) -> Result<()> {
        let conn = self.db.conn();
        conn.execute(
            "UPDATE search_sessions SET current_offset = ?1, results_fetched = ?2 WHERE id = ?3",
            params![offset, fetched, id],
        )?;
        Ok(())
    }

    /// Update session status
    pub fn update_status(&self, id: i64, status: SessionStatus) -> Result<()> {
        let conn = self.db.conn();
        conn.execute(
            "UPDATE search_sessions SET status = ?1 WHERE id = ?2",
            params![status.to_string(), id],
        )?;
        Ok(())
    }

    /// List sessions, optionally filtering by status
    pub fn list(&self, status: Option<SessionStatus>) -> Result<Vec<SearchSession>> {
        let conn = self.db.conn();

        let sql = match status {
            Some(_) => {
                r#"
                SELECT id, query, repository, status, max_results, current_offset, results_fetched, created_at
                FROM search_sessions WHERE status = ?1
                ORDER BY created_at DESC
                "#
            }
            None => {
                r#"
                SELECT id, query, repository, status, max_results, current_offset, results_fetched, created_at
                FROM search_sessions
                ORDER BY created_at DESC
                "#
            }
        };

        let mut stmt = conn.prepare(sql)?;

        let sessions = if let Some(s) = status {
            stmt.query_map([s.to_string()], Self::map_row)?
        } else {
            stmt.query_map([], Self::map_row)?
        };

        sessions
            .collect::<Result<Vec<_>, _>>()
            .context("Failed to list search sessions")
    }

    /// Find resumable sessions (pending or interrupted)
    pub fn find_resumable(&self) -> Result<Vec<SearchSession>> {
        let conn = self.db.conn();
        let mut stmt = conn.prepare(
            r#"
            SELECT id, query, repository, status, max_results, current_offset, results_fetched, created_at
            FROM search_sessions
            WHERE status IN ('pending', 'in_progress', 'interrupted')
            ORDER BY created_at DESC
            "#,
        )?;

        let sessions = stmt.query_map([], Self::map_row)?;
        sessions
            .collect::<Result<Vec<_>, _>>()
            .context("Failed to find resumable sessions")
    }

    fn map_row(row: &rusqlite::Row<'_>) -> rusqlite::Result<SearchSession> {
        let status_str: String = row.get(3)?;
        Ok(SearchSession {
            id: Some(row.get(0)?),
            query: row.get(1)?,
            repository: row.get(2)?,
            status: status_str.parse().unwrap_or(SessionStatus::Pending),
            max_results: row.get(4)?,
            current_offset: row.get(5)?,
            results_fetched: row.get(6)?,
            created_at: row.get(7)?,
        })
    }
}
