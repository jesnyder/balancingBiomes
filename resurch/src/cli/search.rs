//! Search subcommand implementation

use crate::cli::args::SearchArgs;
use crate::db::{Database, PaperRepository, SearchSession, SearchSessionRepository, SessionStatus};
use crate::repos::{
    CrossRefClient, GoogleScholarScraper, OpenAlexClient, Repository, RepositoryType,
    SemanticScholarClient,
};
use crate::util::ProgressReporter;
use anyhow::{Context, Result};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

/// Run the search subcommand
pub async fn run(args: SearchArgs) -> Result<()> {
    let db = Database::open_default()?;

    // Handle --list flag
    if args.list {
        return list_sessions(&db);
    }

    // Handle --resume flag
    if let Some(session_id) = args.resume {
        return resume_session(&db, session_id).await;
    }

    // Start new search
    let query = args.query.as_ref().context("Query is required")?;
    let repo_type: RepositoryType = args.r#where.parse()?;

    println!("Searching {} for: {}", repo_type, query);
    println!("Max results: {}", args.max_results);

    // Create search session
    let session_repo = SearchSessionRepository::new(&db);
    let session =
        SearchSession::new(query, repo_type.to_string()).with_max_results(args.max_results as i32);
    let session_id = session_repo.create(&session)?;

    // Run the search
    run_search(&db, session_id, query, repo_type, args.max_results).await
}

/// List active/resumable sessions
fn list_sessions(db: &Database) -> Result<()> {
    let session_repo = SearchSessionRepository::new(db);
    let sessions = session_repo.find_resumable()?;

    if sessions.is_empty() {
        println!("No active or resumable search sessions.");
        return Ok(());
    }

    println!("Resumable search sessions:");
    println!(
        "{:<6} {:<15} {:<12} {:<10} {:<30}",
        "ID", "Repository", "Status", "Progress", "Query"
    );
    println!("{}", "-".repeat(80));

    for session in sessions {
        let progress = format!(
            "{}/{}",
            session.results_fetched,
            session.max_results.unwrap_or(0)
        );
        let query_preview: String = session.query.chars().take(28).collect();
        println!(
            "{:<6} {:<15} {:<12} {:<10} {}",
            session.id.unwrap_or(0),
            session.repository,
            session.status,
            progress,
            query_preview
        );
    }

    Ok(())
}

/// Resume an interrupted session
async fn resume_session(db: &Database, session_id: i64) -> Result<()> {
    let session_repo = SearchSessionRepository::new(db);
    let session = session_repo.get(session_id)?.context("Session not found")?;

    if session.status == SessionStatus::Completed {
        println!("Session {} is already completed.", session_id);
        return Ok(());
    }

    println!("Resuming session {}", session_id);
    println!("Query: {}", session.query);
    println!("Repository: {}", session.repository);
    println!(
        "Progress: {}/{}",
        session.results_fetched,
        session.max_results.unwrap_or(0)
    );

    let repo_type: RepositoryType = session.repository.parse()?;
    let max_results = session.max_results.unwrap_or(100) as u32;
    let start_offset = session.current_offset as u32;

    run_search_from(
        db,
        session_id,
        &session.query,
        repo_type,
        max_results,
        start_offset,
        session.results_fetched as u32,
    )
    .await
}

/// Run a search from the beginning
async fn run_search(
    db: &Database,
    session_id: i64,
    query: &str,
    repo_type: RepositoryType,
    max_results: u32,
) -> Result<()> {
    run_search_from(db, session_id, query, repo_type, max_results, 0, 0).await
}

/// Run a search from a specific offset
async fn run_search_from(
    db: &Database,
    session_id: i64,
    query: &str,
    repo_type: RepositoryType,
    max_results: u32,
    start_offset: u32,
    start_count: u32,
) -> Result<()> {
    let session_repo = SearchSessionRepository::new(db);
    let paper_repo = PaperRepository::new(db);

    // Set up SIGINT handler
    let interrupted = Arc::new(AtomicBool::new(false));
    let int_flag = interrupted.clone();
    ctrlc::set_handler(move || {
        int_flag.store(true, Ordering::SeqCst);
    })
    .ok();

    // Get repository client
    let repo: Box<dyn Repository> = match repo_type {
        RepositoryType::CrossRef => Box::new(CrossRefClient::new()),
        RepositoryType::OpenAlex => Box::new(OpenAlexClient::new()),
        RepositoryType::SemanticScholar => Box::new(SemanticScholarClient::new()),
        RepositoryType::GoogleScholar => Box::new(GoogleScholarScraper::new()),
    };

    // Mark session as in progress
    session_repo.update_status(session_id, SessionStatus::InProgress)?;

    let batch_size = 20u32;
    let mut offset = start_offset;
    let mut total_fetched = start_count;
    let mut total_new = 0u32;

    let progress = ProgressReporter::new(max_results as u64, "Searching...");
    progress.set_position(total_fetched as u64);

    loop {
        // Check for interrupt
        if interrupted.load(Ordering::SeqCst) {
            progress.abandon("Interrupted");
            println!("\nSearch interrupted. Session saved for resuming.");
            session_repo.update_status(session_id, SessionStatus::Interrupted)?;
            return Ok(());
        }

        // Check if we've hit the limit
        if total_fetched >= max_results {
            break;
        }

        // Calculate how many to fetch
        let remaining = max_results - total_fetched;
        let limit = remaining.min(batch_size);

        // Perform search
        progress.set_message(&format!("Fetching offset {}...", offset));

        let result = match repo.search(query, offset, limit).await {
            Ok(r) => r,
            Err(e) => {
                progress.abandon(&format!("Error: {}", e));
                session_repo.update_status(session_id, SessionStatus::Interrupted)?;
                return Err(e);
            }
        };

        let batch_count = result.papers.len() as u32;

        // Save papers to database
        for paper in &result.papers {
            match paper_repo.insert_or_update(paper) {
                Ok(_) => total_new += 1,
                Err(e) => {
                    tracing::warn!("Failed to save paper: {}", e);
                }
            }
        }

        total_fetched += batch_count;
        offset = result.next_offset.unwrap_or(offset + batch_size);

        // Update session progress
        session_repo.update_progress(session_id, offset as i32, total_fetched as i32)?;

        progress.set_position(total_fetched as u64);

        // Check if repository has more results
        if !result.has_more || batch_count == 0 {
            break;
        }
    }

    // Mark session as completed
    session_repo.update_status(session_id, SessionStatus::Completed)?;

    progress.finish(&format!(
        "Done: {} papers fetched, {} new/updated",
        total_fetched, total_new
    ));

    Ok(())
}
