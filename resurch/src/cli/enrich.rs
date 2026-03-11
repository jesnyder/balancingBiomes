//! Enrich subcommand implementation

use crate::cli::args::EnrichArgs;
use crate::db::{Database, EnrichmentQueue, PaperRepository};
use crate::repos::{CrossRefClient, OpenAlexClient, Repository, SemanticScholarClient};
use crate::util::ProgressReporter;
use anyhow::Result;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

/// Run the enrich subcommand
pub async fn run(args: EnrichArgs) -> Result<()> {
    let db = Database::open_default()?;
    let queue = EnrichmentQueue::new(&db);

    // Handle --status flag
    if args.status {
        return show_status(&db);
    }

    // Handle --queue flag
    if args.queue {
        let count = queue.queue_papers_needing_enrichment()?;
        println!("Queued {} papers for enrichment.", count);
        return Ok(());
    }

    // Run enrichment
    enrich_papers(&db, args.max).await
}

/// Show enrichment queue status
fn show_status(db: &Database) -> Result<()> {
    let queue = EnrichmentQueue::new(db);
    let pending = queue.pending_count()?;

    let paper_repo = PaperRepository::new(db);
    let papers_needing = paper_repo.get_papers_needing_enrichment(1000)?;

    println!("Enrichment Status");
    println!("=================");
    println!("Papers missing DOI or abstract: {}", papers_needing.len());
    println!("In enrichment queue (pending):  {}", pending);

    Ok(())
}

/// Enrich papers with missing metadata
async fn enrich_papers(db: &Database, max: u32) -> Result<()> {
    let paper_repo = PaperRepository::new(db);
    let queue = EnrichmentQueue::new(db);

    // Set up SIGINT handler
    let interrupted = Arc::new(AtomicBool::new(false));
    let int_flag = interrupted.clone();
    ctrlc::set_handler(move || {
        int_flag.store(true, Ordering::SeqCst);
    })
    .ok();

    // Get papers needing enrichment
    let papers = paper_repo.get_papers_needing_enrichment(max)?;

    if papers.is_empty() {
        println!("No papers need enrichment.");
        return Ok(());
    }

    println!("Enriching {} papers...", papers.len());

    // Create API clients
    let crossref = CrossRefClient::new();
    let openalex = OpenAlexClient::new();
    let semantic_scholar = SemanticScholarClient::new();

    let progress = ProgressReporter::new(papers.len() as u64, "Enriching...");
    let mut enriched_count = 0u32;

    for paper in &papers {
        // Check for interrupt
        if interrupted.load(Ordering::SeqCst) {
            progress.abandon("Interrupted");
            println!("\nEnrichment interrupted.");
            return Ok(());
        }

        let paper_id = paper.id.unwrap_or(0);
        let title_preview: String = paper.title.chars().take(40).collect();
        progress.set_message(&format!("{}...", title_preview));

        // Try to enrich with each source
        let mut enriched = paper.clone();
        let mut found_data = false;

        // Try by DOI first if available
        if let Some(ref doi) = paper.doi {
            if !doi.is_empty() {
                // Try CrossRef
                if let Ok(Some(cr_paper)) = crossref.get_by_doi(doi).await {
                    enriched.merge_from(&cr_paper);
                    found_data = true;
                }

                // Try OpenAlex if still missing abstract
                if enriched.abstract_text.is_none() {
                    if let Ok(Some(oa_paper)) = openalex.get_by_doi(doi).await {
                        enriched.merge_from(&oa_paper);
                        found_data = true;
                    }
                }

                // Try Semantic Scholar if still missing abstract
                if enriched.abstract_text.is_none() {
                    if let Ok(Some(ss_paper)) = semantic_scholar.get_by_doi(doi).await {
                        enriched.merge_from(&ss_paper);
                        found_data = true;
                    }
                }
            }
        }

        // Try by title if DOI lookup didn't work or DOI is missing
        if !found_data || enriched.abstract_text.is_none() || enriched.doi.is_none() {
            // Try CrossRef title search
            if let Ok(Some(cr_paper)) = crossref.search_by_title(&paper.title).await {
                enriched.merge_from(&cr_paper);
                found_data = true;
            }

            // Try OpenAlex if still missing data
            if enriched.abstract_text.is_none() {
                if let Ok(Some(oa_paper)) = openalex.search_by_title(&paper.title).await {
                    enriched.merge_from(&oa_paper);
                    found_data = true;
                }
            }
        }

        // Update paper if we found new data
        if found_data {
            if let Err(e) = paper_repo.update(paper_id, &enriched) {
                tracing::warn!("Failed to update paper {}: {}", paper_id, e);
            } else {
                enriched_count += 1;
            }
        }

        // Mark as processed in queue
        queue.mark_completed(paper_id).ok();

        progress.inc();
    }

    progress.finish(&format!(
        "Done: {}/{} papers enriched",
        enriched_count,
        papers.len()
    ));

    Ok(())
}
