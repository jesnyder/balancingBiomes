//! Repository trait definitions

use crate::models::Paper;
use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::str::FromStr;

/// Available repository types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RepositoryType {
    CrossRef,
    OpenAlex,
    SemanticScholar,
    GoogleScholar,
}

impl RepositoryType {
    /// Get all available repository types
    pub fn all() -> Vec<Self> {
        vec![
            Self::CrossRef,
            Self::OpenAlex,
            Self::SemanticScholar,
            Self::GoogleScholar,
        ]
    }

    /// Get the recommended delay between requests for this repository
    pub fn recommended_delay(&self) -> std::time::Duration {
        match self {
            Self::GoogleScholar => std::time::Duration::from_secs(70),
            _ => std::time::Duration::from_secs(2),
        }
    }
}

impl fmt::Display for RepositoryType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::CrossRef => write!(f, "crossref"),
            Self::OpenAlex => write!(f, "openalex"),
            Self::SemanticScholar => write!(f, "semantic_scholar"),
            Self::GoogleScholar => write!(f, "google_scholar"),
        }
    }
}

impl FromStr for RepositoryType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self> {
        match s.to_lowercase().as_str() {
            "crossref" | "cr" => Ok(Self::CrossRef),
            "openalex" | "oa" => Ok(Self::OpenAlex),
            "semantic_scholar" | "semanticscholar" | "ss" | "s2" => Ok(Self::SemanticScholar),
            "google_scholar" | "googlescholar" | "gs" | "gscholar" => Ok(Self::GoogleScholar),
            _ => anyhow::bail!(
                "Unknown repository: {}. Available: crossref, openalex, semantic_scholar, google_scholar",
                s
            ),
        }
    }
}

/// Result from a search operation
#[derive(Debug)]
pub struct SearchResult {
    /// Papers found in this batch
    pub papers: Vec<Paper>,
    /// Total results available (if known)
    pub total_results: Option<u64>,
    /// Whether there are more results
    pub has_more: bool,
    /// Next offset/cursor for pagination
    pub next_offset: Option<u32>,
}

/// Trait for repository implementations
#[async_trait]
pub trait Repository: Send + Sync {
    /// Get the repository type
    fn repository_type(&self) -> RepositoryType;

    /// Search for papers by query
    async fn search(&self, query: &str, offset: u32, limit: u32) -> Result<SearchResult>;

    /// Get paper by DOI
    async fn get_by_doi(&self, doi: &str) -> Result<Option<Paper>>;

    /// Search by title to find matching paper
    async fn search_by_title(&self, title: &str) -> Result<Option<Paper>>;
}
