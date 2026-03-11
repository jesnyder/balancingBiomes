//! CrossRef API client

use super::traits::{Repository, RepositoryType, SearchResult};
use crate::models::Paper;
use crate::util::{clean_text, extract_doi_from_url, RateLimiter};
use anyhow::{Context, Result};
use async_trait::async_trait;
use reqwest::Client;
use serde::Deserialize;

const CROSSREF_API_BASE: &str = "https://api.crossref.org";

/// CrossRef API client
pub struct CrossRefClient {
    client: Client,
    rate_limiter: RateLimiter,
}

impl CrossRefClient {
    pub fn new() -> Self {
        Self {
            client: Client::builder()
                .user_agent(
                    "resurch/0.1.0 (https://github.com/resurch; mailto:resurch@example.com)",
                )
                .build()
                .expect("Failed to build HTTP client"),
            rate_limiter: RateLimiter::standard_api(),
        }
    }
}

impl Default for CrossRefClient {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Repository for CrossRefClient {
    fn repository_type(&self) -> RepositoryType {
        RepositoryType::CrossRef
    }

    async fn search(&self, query: &str, offset: u32, limit: u32) -> Result<SearchResult> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works", CROSSREF_API_BASE);

        let response = self
            .client
            .get(&url)
            .query(&[
                ("query", query),
                ("rows", &limit.to_string()),
                ("offset", &offset.to_string()),
            ])
            .send()
            .await
            .context("Failed to send CrossRef search request")?;

        if !response.status().is_success() {
            anyhow::bail!("CrossRef API error: {}", response.status());
        }

        let data: CrossRefSearchResponse = response
            .json()
            .await
            .context("Failed to parse CrossRef response")?;

        let total_results = Some(data.message.total_results as u64);
        let papers: Vec<Paper> = data.message.items.into_iter().map(work_to_paper).collect();

        let has_more = (offset as u64 + papers.len() as u64) < data.message.total_results as u64;

        Ok(SearchResult {
            papers,
            total_results,
            has_more,
            next_offset: if has_more { Some(offset + limit) } else { None },
        })
    }

    async fn get_by_doi(&self, doi: &str) -> Result<Option<Paper>> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works/{}", CROSSREF_API_BASE, doi);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .context("Failed to send CrossRef DOI request")?;

        if response.status().as_u16() == 404 {
            return Ok(None);
        }

        if !response.status().is_success() {
            anyhow::bail!("CrossRef API error: {}", response.status());
        }

        let data: CrossRefWorkResponse = response
            .json()
            .await
            .context("Failed to parse CrossRef work response")?;

        Ok(Some(work_to_paper(data.message)))
    }

    async fn search_by_title(&self, title: &str) -> Result<Option<Paper>> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works", CROSSREF_API_BASE);

        let response = self
            .client
            .get(&url)
            .query(&[("query.title", title), ("rows", "1")])
            .send()
            .await
            .context("Failed to send CrossRef title search request")?;

        if !response.status().is_success() {
            anyhow::bail!("CrossRef API error: {}", response.status());
        }

        let data: CrossRefSearchResponse = response
            .json()
            .await
            .context("Failed to parse CrossRef response")?;

        Ok(data.message.items.into_iter().next().map(work_to_paper))
    }
}

fn work_to_paper(work: CrossRefWork) -> Paper {
    let title = work.title.into_iter().next().unwrap_or_default();

    let doi = work.doi.clone();
    let doi_url = doi.as_ref().map(|d| format!("https://doi.org/{}", d));

    // Try to extract DOI from URL if not present
    let doi = doi.or_else(|| work.url.as_ref().and_then(|u| extract_doi_from_url(u)));

    let abstract_text = work.r#abstract.map(|a| clean_text(&a));

    let year = work
        .published_print
        .or(work.published_online)
        .or(work.created)
        .and_then(|d| d.date_parts.into_iter().next())
        .and_then(|parts| parts.into_iter().next())
        .map(|y| y as u16);

    let authors = work
        .author
        .unwrap_or_default()
        .into_iter()
        .map(|a| match (a.given, a.family) {
            (Some(given), Some(family)) => format!("{} {}", given, family),
            (None, Some(family)) => family,
            (Some(given), None) => given,
            (None, None) => String::new(),
        })
        .filter(|s| !s.is_empty())
        .collect();

    let publication = work.container_title.into_iter().next();

    Paper {
        id: None,
        doi,
        title,
        title_normalized: None,
        citations: work.is_referenced_by_count.unwrap_or(0) as i32,
        year,
        publication,
        abstract_text,
        snippet: None,
        publisher_url: work.url,
        doi_url,
        source_repository: Some("crossref".to_string()),
        raw_json: None,
        authors,
        publisher: work.publisher,
        created_at: None,
        updated_at: None,
    }
}

// CrossRef API response types

#[derive(Debug, Deserialize)]
struct CrossRefSearchResponse {
    message: CrossRefSearchMessage,
}

#[derive(Debug, Deserialize)]
struct CrossRefSearchMessage {
    #[serde(default)]
    items: Vec<CrossRefWork>,
    #[serde(rename = "total-results", default)]
    total_results: i64,
}

#[derive(Debug, Deserialize)]
struct CrossRefWorkResponse {
    message: CrossRefWork,
}

#[derive(Debug, Deserialize)]
struct CrossRefWork {
    #[serde(rename = "DOI")]
    doi: Option<String>,
    #[serde(default)]
    title: Vec<String>,
    #[serde(rename = "abstract")]
    r#abstract: Option<String>,
    #[serde(rename = "container-title", default)]
    container_title: Vec<String>,
    publisher: Option<String>,
    #[serde(rename = "is-referenced-by-count")]
    is_referenced_by_count: Option<i64>,
    #[serde(rename = "URL")]
    url: Option<String>,
    author: Option<Vec<CrossRefAuthor>>,
    #[serde(rename = "published-print")]
    published_print: Option<CrossRefDate>,
    #[serde(rename = "published-online")]
    published_online: Option<CrossRefDate>,
    created: Option<CrossRefDate>,
}

#[derive(Debug, Deserialize)]
struct CrossRefAuthor {
    given: Option<String>,
    family: Option<String>,
}

#[derive(Debug, Deserialize)]
struct CrossRefDate {
    #[serde(rename = "date-parts", default)]
    date_parts: Vec<Vec<i32>>,
}
