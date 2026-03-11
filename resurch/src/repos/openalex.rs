//! OpenAlex API client

use super::traits::{Repository, RepositoryType, SearchResult};
use crate::models::Paper;
use crate::util::{clean_text, RateLimiter};
use anyhow::{Context, Result};
use async_trait::async_trait;
use reqwest::Client;
use serde::Deserialize;
use std::collections::HashMap;

const OPENALEX_API_BASE: &str = "https://api.openalex.org";

/// OpenAlex API client
pub struct OpenAlexClient {
    client: Client,
    rate_limiter: RateLimiter,
}

impl OpenAlexClient {
    pub fn new() -> Self {
        Self {
            client: Client::builder()
                .user_agent("resurch/0.1.0 (mailto:resurch@example.com)")
                .build()
                .expect("Failed to build HTTP client"),
            rate_limiter: RateLimiter::standard_api(),
        }
    }
}

impl Default for OpenAlexClient {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Repository for OpenAlexClient {
    fn repository_type(&self) -> RepositoryType {
        RepositoryType::OpenAlex
    }

    async fn search(&self, query: &str, offset: u32, limit: u32) -> Result<SearchResult> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works", OPENALEX_API_BASE);

        let response = self
            .client
            .get(&url)
            .query(&[
                ("search", query),
                ("per-page", &limit.to_string()),
                ("page", &((offset / limit) + 1).to_string()),
            ])
            .send()
            .await
            .context("Failed to send OpenAlex search request")?;

        if !response.status().is_success() {
            anyhow::bail!("OpenAlex API error: {}", response.status());
        }

        let data: OpenAlexSearchResponse = response
            .json()
            .await
            .context("Failed to parse OpenAlex response")?;

        let total_results = data.meta.as_ref().map(|m| m.count as u64);
        let papers: Vec<Paper> = data.results.into_iter().map(work_to_paper).collect();

        let has_more = total_results
            .map(|total| (offset as u64 + papers.len() as u64) < total)
            .unwrap_or(false);

        Ok(SearchResult {
            papers,
            total_results,
            has_more,
            next_offset: if has_more { Some(offset + limit) } else { None },
        })
    }

    async fn get_by_doi(&self, doi: &str) -> Result<Option<Paper>> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works/doi:{}", OPENALEX_API_BASE, doi);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .context("Failed to send OpenAlex DOI request")?;

        if response.status().as_u16() == 404 {
            return Ok(None);
        }

        if !response.status().is_success() {
            anyhow::bail!("OpenAlex API error: {}", response.status());
        }

        let work: OpenAlexWork = response
            .json()
            .await
            .context("Failed to parse OpenAlex work response")?;

        Ok(Some(work_to_paper(work)))
    }

    async fn search_by_title(&self, title: &str) -> Result<Option<Paper>> {
        self.rate_limiter.wait().await;

        let url = format!("{}/works", OPENALEX_API_BASE);
        let filter = format!("title.search:{}", title);
        let per_page = "1".to_string();

        let response = self
            .client
            .get(&url)
            .query(&[("filter", &filter), ("per-page", &per_page)])
            .send()
            .await
            .context("Failed to send OpenAlex title search request")?;

        if !response.status().is_success() {
            anyhow::bail!("OpenAlex API error: {}", response.status());
        }

        let data: OpenAlexSearchResponse = response
            .json()
            .await
            .context("Failed to parse OpenAlex response")?;

        Ok(data.results.into_iter().next().map(work_to_paper))
    }
}

fn work_to_paper(work: OpenAlexWork) -> Paper {
    let title = work.title.unwrap_or_default();

    // Extract DOI from the ID or doi field
    let doi = work.doi.and_then(|d| {
        d.strip_prefix("https://doi.org/")
            .map(|s| s.to_string())
            .or(Some(d))
    });

    let doi_url = doi.as_ref().map(|d| format!("https://doi.org/{}", d));

    // Reconstruct abstract from inverted index
    let abstract_text = work.abstract_inverted_index.map(invert_abstract_index);

    let year = work.publication_year.map(|y| y as u16);

    let authors = work
        .authorships
        .unwrap_or_default()
        .into_iter()
        .filter_map(|a| a.author.and_then(|auth| auth.display_name))
        .collect();

    let (publication, publisher, publisher_url) = match work.primary_location {
        Some(loc) => {
            let url = loc.landing_page_url;
            match loc.source {
                Some(src) => (src.display_name, src.host_organization_name, url),
                None => (None, None, url),
            }
        }
        None => (None, None, None),
    };

    Paper {
        id: None,
        doi,
        title: clean_text(&title),
        title_normalized: None,
        citations: work.cited_by_count.unwrap_or(0) as i32,
        year,
        publication,
        abstract_text,
        snippet: None,
        publisher_url,
        doi_url,
        source_repository: Some("openalex".to_string()),
        raw_json: None,
        authors,
        publisher,
        created_at: None,
        updated_at: None,
    }
}

/// Reconstruct abstract from inverted index
fn invert_abstract_index(inverted_index: HashMap<String, Vec<usize>>) -> String {
    if inverted_index.is_empty() {
        return String::new();
    }

    // Find max position
    let max_position = inverted_index
        .values()
        .flat_map(|positions| positions.iter())
        .max()
        .copied()
        .unwrap_or(0);

    // Create word array
    let mut words = vec![String::new(); max_position + 1];

    // Place each word at its positions
    for (word, positions) in inverted_index {
        for pos in positions {
            if pos < words.len() {
                words[pos] = word.clone();
            }
        }
    }

    // Join words and clean
    clean_text(&words.join(" "))
}

// OpenAlex API response types

#[derive(Debug, Deserialize)]
struct OpenAlexSearchResponse {
    meta: Option<OpenAlexMeta>,
    #[serde(default)]
    results: Vec<OpenAlexWork>,
}

#[derive(Debug, Deserialize)]
struct OpenAlexMeta {
    count: i64,
}

#[derive(Debug, Deserialize)]
struct OpenAlexWork {
    title: Option<String>,
    doi: Option<String>,
    publication_year: Option<i32>,
    cited_by_count: Option<i64>,
    abstract_inverted_index: Option<HashMap<String, Vec<usize>>>,
    authorships: Option<Vec<OpenAlexAuthorship>>,
    primary_location: Option<OpenAlexLocation>,
}

#[derive(Debug, Deserialize)]
struct OpenAlexLocation {
    landing_page_url: Option<String>,
    source: Option<OpenAlexSource>,
}

#[derive(Debug, Deserialize)]
struct OpenAlexSource {
    display_name: Option<String>,
    host_organization_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct OpenAlexAuthorship {
    author: Option<OpenAlexAuthor>,
}

#[derive(Debug, Deserialize)]
struct OpenAlexAuthor {
    display_name: Option<String>,
}
