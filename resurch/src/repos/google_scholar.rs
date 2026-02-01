//! Google Scholar HTML scraper

use super::traits::{Repository, RepositoryType, SearchResult};
use crate::models::Paper;
use crate::util::{clean_text, extract_doi_from_url, RateLimiter};
use anyhow::{Context, Result};
use async_trait::async_trait;
use regex::Regex;
use reqwest::Client;
use scraper::{Html, Selector};
use std::sync::LazyLock;

const GOOGLE_SCHOLAR_BASE: &str = "https://scholar.google.com/scholar";

/// Selector for result items
static RESULT_SELECTOR: LazyLock<Selector> =
    LazyLock::new(|| Selector::parse("div.gs_ri").expect("Invalid selector"));

/// Selector for title
static TITLE_SELECTOR: LazyLock<Selector> =
    LazyLock::new(|| Selector::parse("h3.gs_rt").expect("Invalid selector"));

/// Selector for author/year info
static AUTHOR_SELECTOR: LazyLock<Selector> =
    LazyLock::new(|| Selector::parse("div.gs_a").expect("Invalid selector"));

/// Selector for snippet
static SNIPPET_SELECTOR: LazyLock<Selector> =
    LazyLock::new(|| Selector::parse("div.gs_rs").expect("Invalid selector"));

/// Selector for citation count
static CITE_SELECTOR: LazyLock<Selector> =
    LazyLock::new(|| Selector::parse("div.gs_fl a").expect("Invalid selector"));

/// Regex for extracting citation count
static CITE_PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"Cited by (\d+)").expect("Invalid regex"));

/// Regex for extracting year from author line
static YEAR_PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(19|20)\d{2}\b").expect("Invalid regex"));

/// Google Scholar HTML scraper
///
/// Warning: Use with extreme caution. Google Scholar aggressively rate-limits
/// and may block IP addresses. Use 70+ second delays between requests.
pub struct GoogleScholarScraper {
    client: Client,
    rate_limiter: RateLimiter,
}

impl GoogleScholarScraper {
    pub fn new() -> Self {
        Self {
            client: Client::builder()
                .user_agent(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                     AppleWebKit/537.36 (KHTML, like Gecko) \
                     Chrome/120.0.0.0 Safari/537.36",
                )
                .build()
                .expect("Failed to build HTTP client"),
            rate_limiter: RateLimiter::google_scholar(),
        }
    }
}

impl Default for GoogleScholarScraper {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Repository for GoogleScholarScraper {
    fn repository_type(&self) -> RepositoryType {
        RepositoryType::GoogleScholar
    }

    async fn search(&self, query: &str, offset: u32, limit: u32) -> Result<SearchResult> {
        self.rate_limiter.wait().await;

        // Google Scholar uses 'start' for pagination, showing 10 results per page
        let response = self
            .client
            .get(GOOGLE_SCHOLAR_BASE)
            .query(&[("q", query), ("hl", "en"), ("start", &offset.to_string())])
            .send()
            .await
            .context("Failed to send Google Scholar request")?;

        let status = response.status();
        if status.as_u16() == 429 {
            anyhow::bail!("Google Scholar rate limit exceeded (HTTP 429). Wait and retry.");
        }
        if status.as_u16() == 503 || status.as_u16() == 403 {
            anyhow::bail!(
                "Google Scholar blocked request (HTTP {}). Your IP may be temporarily blocked.",
                status
            );
        }
        if !status.is_success() {
            anyhow::bail!("Google Scholar error: {}", status);
        }

        let html = response
            .text()
            .await
            .context("Failed to read Google Scholar response")?;

        let papers = parse_scholar_html(&html);
        let result_count = papers.len();

        // Google Scholar doesn't tell us total results reliably
        // Assume there are more if we got a full page
        let has_more = result_count >= 10;

        Ok(SearchResult {
            papers: papers.into_iter().take(limit as usize).collect(),
            total_results: None,
            has_more,
            next_offset: if has_more {
                Some(offset + 10) // Scholar pages by 10
            } else {
                None
            },
        })
    }

    async fn get_by_doi(&self, _doi: &str) -> Result<Option<Paper>> {
        // Google Scholar doesn't support DOI lookup directly
        Ok(None)
    }

    async fn search_by_title(&self, title: &str) -> Result<Option<Paper>> {
        let result = self.search(&format!("\"{}\"", title), 0, 1).await?;
        Ok(result.papers.into_iter().next())
    }
}

/// Parse Google Scholar HTML and extract papers
fn parse_scholar_html(html: &str) -> Vec<Paper> {
    let document = Html::parse_document(html);
    let mut papers = Vec::new();

    for result in document.select(&RESULT_SELECTOR) {
        let mut paper = Paper {
            source_repository: Some("google_scholar".to_string()),
            ..Default::default()
        };

        // Extract title and link
        if let Some(title_elem) = result.select(&TITLE_SELECTOR).next() {
            let title_text = title_elem.text().collect::<String>();
            paper.title = clean_text(&title_text);

            // Extract link from <a> tag
            if let Some(link) = title_elem.select(&Selector::parse("a").unwrap()).next() {
                if let Some(href) = link.value().attr("href") {
                    paper.publisher_url = Some(href.to_string());

                    // Try to extract DOI from URL
                    if let Some(doi) = extract_doi_from_url(href) {
                        paper.doi = Some(doi.clone());
                        paper.doi_url = Some(format!("https://doi.org/{}", doi));
                    }
                }
            }
        }

        // Extract author/year info
        if let Some(author_elem) = result.select(&AUTHOR_SELECTOR).next() {
            let author_text = author_elem.text().collect::<String>();

            // Extract year
            if let Some(caps) = YEAR_PATTERN.captures(&author_text) {
                if let Some(year_str) = caps.get(0) {
                    paper.year = year_str.as_str().parse().ok();
                }
            }
        }

        // Extract snippet
        if let Some(snippet_elem) = result.select(&SNIPPET_SELECTOR).next() {
            let snippet_text = snippet_elem.text().collect::<String>();
            paper.snippet = Some(clean_text(&snippet_text));
        }

        // Extract citation count
        for link in result.select(&CITE_SELECTOR) {
            let link_text = link.text().collect::<String>();
            if let Some(caps) = CITE_PATTERN.captures(&link_text) {
                if let Some(count_str) = caps.get(1) {
                    paper.citations = count_str.as_str().parse().unwrap_or(0);
                    break;
                }
            }
        }

        // Only add if we got a title
        if !paper.title.is_empty() {
            paper.title_normalized = Some(Paper::normalize_title(&paper.title));
            papers.push(paper);
        }
    }

    papers
}
