//! HTML text cleaning utilities

use regex::Regex;
use std::sync::LazyLock;

/// Pattern for HTML tags
static HTML_TAG_PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"<[^>]+>").expect("Invalid HTML tag regex"));

/// Pattern for format markers like [HTML], [PDF], [BOOK], etc.
static FORMAT_MARKER_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\[(?:HTML|PDF|BOOK|B|XML|DOC|CITATION)\]").expect("Invalid format marker regex")
});

/// Clean text by removing HTML tags, format markers, and normalizing whitespace
///
/// - Removes HTML tags like `<b>`, `<i>`, `<em>`
/// - Decodes HTML entities like `&amp;`, `&lt;`
/// - Removes format markers like `[HTML]`, `[PDF]`
/// - Normalizes whitespace
pub fn clean_text(text: &str) -> String {
    if text.is_empty() {
        return String::new();
    }

    // Remove HTML tags
    let text = HTML_TAG_PATTERN.replace_all(text, "");

    // Decode HTML entities
    let text = html_escape::decode_html_entities(&text);

    // Remove format markers
    let text = FORMAT_MARKER_PATTERN.replace_all(&text, "");

    // Normalize whitespace
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// Reconstruct abstract from OpenAlex inverted index format
///
/// OpenAlex stores abstracts as inverted indices:
/// `{"word1": [0, 5], "word2": [1, 3]}` means:
/// - "word1" appears at positions 0 and 5
/// - "word2" appears at positions 1 and 3
pub fn invert_abstract_index(
    inverted_index: &std::collections::HashMap<String, Vec<usize>>,
) -> String {
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
        for &pos in positions {
            if pos < words.len() {
                words[pos] = word.clone();
            }
        }
    }

    // Join words
    words.join(" ")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_clean_text_html_tags() {
        assert_eq!(clean_text("<b>bold</b> text"), "bold text");
        assert_eq!(clean_text("<em>italic</em>"), "italic");
    }

    #[test]
    fn test_clean_text_html_entities() {
        assert_eq!(clean_text("foo &amp; bar"), "foo & bar");
        assert_eq!(clean_text("&lt;tag&gt;"), "<tag>");
    }

    #[test]
    fn test_clean_text_format_markers() {
        assert_eq!(clean_text("[PDF] Article Title"), "Article Title");
        assert_eq!(clean_text("[HTML] [BOOK] Title"), "Title");
    }

    #[test]
    fn test_clean_text_whitespace() {
        assert_eq!(clean_text("  multiple   spaces  "), "multiple spaces");
        assert_eq!(clean_text("line\nbreak"), "line break");
    }

    #[test]
    fn test_invert_abstract_index() {
        let mut index = std::collections::HashMap::new();
        index.insert("hello".to_string(), vec![0]);
        index.insert("world".to_string(), vec![1]);

        assert_eq!(invert_abstract_index(&index), "hello world");
    }
}
