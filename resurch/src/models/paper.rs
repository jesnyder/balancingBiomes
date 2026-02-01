//! Paper model representing an academic paper

use serde::{Deserialize, Serialize};

/// Represents an academic paper with metadata
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Paper {
    /// Database ID (None if not yet persisted)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<i64>,

    /// Digital Object Identifier
    #[serde(skip_serializing_if = "Option::is_none")]
    pub doi: Option<String>,

    /// Paper title
    pub title: String,

    /// Normalized title for deduplication (lowercase, no punctuation)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub title_normalized: Option<String>,

    /// Citation count
    #[serde(default)]
    pub citations: i32,

    /// Publication year
    #[serde(skip_serializing_if = "Option::is_none")]
    pub year: Option<u16>,

    /// Journal/venue name
    #[serde(skip_serializing_if = "Option::is_none")]
    pub publication: Option<String>,

    /// Paper abstract
    #[serde(skip_serializing_if = "Option::is_none")]
    pub abstract_text: Option<String>,

    /// Short snippet from search results
    #[serde(skip_serializing_if = "Option::is_none")]
    pub snippet: Option<String>,

    /// Publisher URL
    #[serde(skip_serializing_if = "Option::is_none")]
    pub publisher_url: Option<String>,

    /// DOI URL (https://doi.org/...)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub doi_url: Option<String>,

    /// Source repository (crossref, openalex, semantic_scholar, google_scholar)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_repository: Option<String>,

    /// Raw JSON response from API
    #[serde(skip_serializing_if = "Option::is_none")]
    pub raw_json: Option<String>,

    /// Authors list
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub authors: Vec<String>,

    /// Publisher name
    #[serde(skip_serializing_if = "Option::is_none")]
    pub publisher: Option<String>,

    /// Creation timestamp
    #[serde(skip_serializing_if = "Option::is_none")]
    pub created_at: Option<String>,

    /// Last update timestamp
    #[serde(skip_serializing_if = "Option::is_none")]
    pub updated_at: Option<String>,
}

impl Paper {
    /// Create a new paper with just a title
    pub fn new(title: impl Into<String>) -> Self {
        let title = title.into();
        let title_normalized = Some(Self::normalize_title(&title));
        Self {
            title,
            title_normalized,
            ..Default::default()
        }
    }

    /// Normalize a title for deduplication
    /// - Lowercase
    /// - Remove punctuation
    /// - Collapse whitespace
    pub fn normalize_title(title: &str) -> String {
        title
            .to_lowercase()
            .chars()
            .filter(|c| c.is_alphanumeric() || c.is_whitespace())
            .collect::<String>()
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
    }

    /// Get the DOI URL, constructing it from DOI if needed
    pub fn get_doi_url(&self) -> Option<String> {
        self.doi_url.clone().or_else(|| {
            self.doi
                .as_ref()
                .map(|doi| format!("https://doi.org/{}", doi))
        })
    }

    /// Check if this paper has sufficient metadata
    pub fn has_metadata(&self) -> bool {
        self.abstract_text.is_some() || self.doi.is_some()
    }

    /// Merge metadata from another paper (enrichment)
    pub fn merge_from(&mut self, other: &Paper) {
        if self.doi.is_none() && other.doi.is_some() {
            self.doi = other.doi.clone();
            self.doi_url = other.doi_url.clone();
        }
        if self.abstract_text.is_none() && other.abstract_text.is_some() {
            self.abstract_text = other.abstract_text.clone();
        }
        if self.year.is_none() && other.year.is_some() {
            self.year = other.year;
        }
        if self.publication.is_none() && other.publication.is_some() {
            self.publication = other.publication.clone();
        }
        if self.publisher.is_none() && other.publisher.is_some() {
            self.publisher = other.publisher.clone();
        }
        if self.citations == 0 && other.citations > 0 {
            self.citations = other.citations;
        }
        if self.authors.is_empty() && !other.authors.is_empty() {
            self.authors = other.authors.clone();
        }
    }
}
