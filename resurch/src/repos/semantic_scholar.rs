//! Semantic Scholar API client

use super::traits::{Repository, RepositoryType, SearchResult};
use crate::models::Paper;
use crate::util::{clean_text, RateLimiter};
use anyhow::{Context, Result};
use async_trait::async_trait;
use reqwest::Client;
use serde::Deserialize;

const SEMANTIC_SCHOLAR_API_BASE: &str = "https://api.semanticscholar.org/graph/v1";

/// Semantic Scholar API client
pub struct SemanticScholarClient {
    client: Client,
    rate_limiter: RateLimiter,
}

impl SemanticScholarClient {
    pub fn new() -> Self {
        Self {
            client: Client::builder()
                .user_agent("resurch/0.1.0")
                .build()
                .expect("Failed to build HTTP client"),
            rate_limiter: RateLimiter::standard_api(),
        }
    }
}

impl Default for SemanticScholarClient {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Repository for SemanticScholarClient {
    fn repository_type(&self) -> RepositoryType {
        RepositoryType::SemanticScholar
    }

    async fn search(&self, query: &str, offset: u32, limit: u32) -> Result<SearchResult> {
        self.rate_limiter.wait().await;

        let url = format!("{}/paper/search", SEMANTIC_SCHOLAR_API_BASE);

        let response = self
            .client
            .get(&url)
            .query(&[
                ("query", query),
                ("limit", &limit.to_string()),
                ("offset", &offset.to_string()),
                (
                    "fields",
                    "paperId,title,abstract,year,citationCount,authors,venue,externalIds,url",
                ),
            ])
            .send()
            .await
            .context("Failed to send Semantic Scholar search request")?;

        if !response.status().is_success() {
            anyhow::bail!("Semantic Scholar API error: {}", response.status());
        }

        let data: S2SearchResponse = response
            .json()
            .await
            .context("Failed to parse Semantic Scholar response")?;

        let total_results = Some(data.total as u64);
        let papers: Vec<Paper> = data.data.into_iter().map(paper_to_paper).collect();

        let has_more = (offset as u64 + papers.len() as u64) < data.total as u64;

        Ok(SearchResult {
            papers,
            total_results,
            has_more,
            next_offset: if has_more { Some(offset + limit) } else { None },
        })
    }

    async fn get_by_doi(&self, doi: &str) -> Result<Option<Paper>> {
        self.rate_limiter.wait().await;

        let url = format!("{}/paper/DOI:{}", SEMANTIC_SCHOLAR_API_BASE, doi);

        let response = self
            .client
            .get(&url)
            .query(&[(
                "fields",
                "paperId,title,abstract,year,citationCount,authors,venue,externalIds,url",
            )])
            .send()
            .await
            .context("Failed to send Semantic Scholar DOI request")?;

        if response.status().as_u16() == 404 {
            return Ok(None);
        }

        if !response.status().is_success() {
            anyhow::bail!("Semantic Scholar API error: {}", response.status());
        }

        let paper: S2Paper = response
            .json()
            .await
            .context("Failed to parse Semantic Scholar paper response")?;

        Ok(Some(paper_to_paper(paper)))
    }

    async fn search_by_title(&self, title: &str) -> Result<Option<Paper>> {
        // Semantic Scholar's search works well with titles
        let result = self.search(title, 0, 1).await?;
        Ok(result.papers.into_iter().next())
    }
}

fn paper_to_paper(s2: S2Paper) -> Paper {
    let doi = s2.external_ids.as_ref().and_then(|ids| ids.doi.clone());

    let doi_url = doi.as_ref().map(|d| format!("https://doi.org/{}", d));

    let abstract_text = s2.r#abstract.map(|a| clean_text(&a));

    let authors = s2
        .authors
        .unwrap_or_default()
        .into_iter()
        .filter_map(|a| a.name)
        .collect();

    Paper {
        id: None,
        doi,
        title: clean_text(&s2.title.unwrap_or_default()),
        title_normalized: None,
        citations: s2.citation_count.unwrap_or(0) as i32,
        year: s2.year.map(|y| y as u16),
        publication: s2.venue,
        abstract_text,
        snippet: None,
        publisher_url: s2.url,
        doi_url,
        source_repository: Some("semantic_scholar".to_string()),
        raw_json: None,
        authors,
        publisher: None,
        created_at: None,
        updated_at: None,
    }
}

// Semantic Scholar API response types

#[derive(Debug, Deserialize)]
struct S2SearchResponse {
    total: i64,
    #[serde(default)]
    data: Vec<S2Paper>,
}

#[derive(Debug, Deserialize)]
struct S2Paper {
    title: Option<String>,
    #[serde(rename = "abstract")]
    r#abstract: Option<String>,
    year: Option<i32>,
    #[serde(rename = "citationCount")]
    citation_count: Option<i64>,
    venue: Option<String>,
    url: Option<String>,
    authors: Option<Vec<S2Author>>,
    #[serde(rename = "externalIds")]
    external_ids: Option<S2ExternalIds>,
}

#[derive(Debug, Deserialize)]
struct S2Author {
    name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct S2ExternalIds {
    #[serde(rename = "DOI")]
    doi: Option<String>,
}
