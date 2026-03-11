//! DOI extraction utilities

use regex::Regex;
use std::sync::LazyLock;

/// Regex pattern for DOI extraction
/// DOI format: 10.XXXX/suffix where XXXX is 4-9 digits
static DOI_PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"10\.\d{4,9}/[^\s"<>]+"#).expect("Invalid DOI regex"));

/// Extract a DOI from a URL or text
///
/// Handles various formats:
/// - DOI at end of URL
/// - DOI in middle of URL
/// - Removes common suffixes like .pdf, /full, /abstract
///
/// # Examples
/// ```
/// use resurch::util::extract_doi_from_url;
///
/// let doi = extract_doi_from_url("https://doi.org/10.1002/abc123");
/// assert_eq!(doi, Some("10.1002/abc123".to_string()));
/// ```
pub fn extract_doi_from_url(url: &str) -> Option<String> {
    if url.is_empty() {
        return None;
    }

    let captures = DOI_PATTERN.find(url)?;

    let mut doi = captures.as_str().to_string();

    // Clean up the DOI
    // Remove trailing punctuation
    while doi.ends_with(['.', ',', ';', ':', ')', ']', '}']) {
        doi.pop();
    }

    // Remove common URL suffixes
    for suffix in &[".pdf", "/full", "/abstract", "/pdf", ".html", "/html"] {
        if doi.ends_with(suffix) {
            doi.truncate(doi.len() - suffix.len());
        }
    }

    // Remove trailing slash
    if doi.ends_with('/') {
        doi.pop();
    }

    // Remove URL query parameters
    if let Some(pos) = doi.find('?') {
        doi.truncate(pos);
    }

    // Remove URL fragments
    if let Some(pos) = doi.find('#') {
        doi.truncate(pos);
    }

    if doi.is_empty() {
        None
    } else {
        Some(doi)
    }
}

/// Construct DOI URL from DOI
pub fn doi_to_url(doi: &str) -> String {
    format!("https://doi.org/{}", doi)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_doi_basic() {
        assert_eq!(
            extract_doi_from_url("https://doi.org/10.1002/abc123"),
            Some("10.1002/abc123".to_string())
        );
    }

    #[test]
    fn test_extract_doi_with_pdf_suffix() {
        assert_eq!(
            extract_doi_from_url("https://example.com/10.1007/1-4020-4018-0.pdf"),
            Some("10.1007/1-4020-4018-0".to_string())
        );
    }

    #[test]
    fn test_extract_doi_with_full_suffix() {
        assert_eq!(
            extract_doi_from_url("https://frontiersin.org/articles/10.3389/fmicb.2018.00148/full"),
            Some("10.3389/fmicb.2018.00148".to_string())
        );
    }

    #[test]
    fn test_extract_doi_complex() {
        assert_eq!(
            extract_doi_from_url(
                "https://onlinelibrary.wiley.com/doi/abs/10.1002/9780470015902.a0000394.pub3"
            ),
            Some("10.1002/9780470015902.a0000394.pub3".to_string())
        );
    }

    #[test]
    fn test_extract_doi_none() {
        assert_eq!(extract_doi_from_url("https://example.com/article"), None);
        assert_eq!(extract_doi_from_url(""), None);
    }
}
