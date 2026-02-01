//! Repository implementations for academic paper sources

mod crossref;
mod google_scholar;
mod openalex;
mod semantic_scholar;
mod traits;

pub use crossref::CrossRefClient;
pub use google_scholar::GoogleScholarScraper;
pub use openalex::OpenAlexClient;
pub use semantic_scholar::SemanticScholarClient;
pub use traits::{Repository, RepositoryType};

#[allow(unused_imports)]
pub use traits::SearchResult;
