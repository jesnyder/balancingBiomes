//! Stats subcommand implementation

use crate::cli::args::StatsArgs;
use crate::db::Database;
use anyhow::Result;

/// Run the stats subcommand
pub async fn run(args: StatsArgs) -> Result<()> {
    let db = Database::open_default()?;
    let stats = db.stats()?;

    println!("{}", stats);

    if args.verbose {
        print_verbose_stats(&db)?;
    }

    Ok(())
}

/// Print verbose statistics
fn print_verbose_stats(db: &Database) -> Result<()> {
    let conn = db.conn();

    println!("\nPapers by Source");
    println!("----------------");
    let mut stmt = conn.prepare(
        "SELECT source_repository, COUNT(*) as count FROM papers GROUP BY source_repository ORDER BY count DESC",
    )?;
    let rows = stmt.query_map([], |row| {
        Ok((
            row.get::<_, Option<String>>(0)?
                .unwrap_or_else(|| "unknown".to_string()),
            row.get::<_, i64>(1)?,
        ))
    })?;
    for row in rows {
        let (source, count) = row?;
        println!("  {}: {}", source, count);
    }

    println!("\nPapers by Year (top 10)");
    println!("-----------------------");
    let mut stmt = conn.prepare(
        "SELECT year, COUNT(*) as count FROM papers WHERE year IS NOT NULL GROUP BY year ORDER BY count DESC LIMIT 10",
    )?;
    let rows = stmt.query_map([], |row| Ok((row.get::<_, i32>(0)?, row.get::<_, i64>(1)?)))?;
    for row in rows {
        let (year, count) = row?;
        println!("  {}: {}", year, count);
    }

    println!("\nTop 10 Most Cited Papers");
    println!("------------------------");
    let mut stmt =
        conn.prepare("SELECT title, citations, year FROM papers ORDER BY citations DESC LIMIT 10")?;
    let rows = stmt.query_map([], |row| {
        Ok((
            row.get::<_, String>(0)?,
            row.get::<_, i32>(1)?,
            row.get::<_, Option<i32>>(2)?,
        ))
    })?;
    for row in rows {
        let (title, citations, year) = row?;
        let title_preview: String = title.chars().take(50).collect();
        let year_str = year
            .map(|y| y.to_string())
            .unwrap_or_else(|| "?".to_string());
        println!("  [{}] ({}) {}", citations, year_str, title_preview);
    }

    println!("\nRecent Search Sessions");
    println!("----------------------");
    let mut stmt = conn.prepare(
        "SELECT id, query, repository, status, results_fetched, created_at FROM search_sessions ORDER BY created_at DESC LIMIT 5",
    )?;
    let rows = stmt.query_map([], |row| {
        Ok((
            row.get::<_, i64>(0)?,
            row.get::<_, String>(1)?,
            row.get::<_, String>(2)?,
            row.get::<_, String>(3)?,
            row.get::<_, i32>(4)?,
            row.get::<_, String>(5)?,
        ))
    })?;
    for row in rows {
        let (id, query, repo, status, fetched, _created) = row?;
        let query_preview: String = query.chars().take(30).collect();
        println!(
            "  #{} [{}] {}: {} (fetched: {})",
            id, status, repo, query_preview, fetched
        );
    }

    Ok(())
}
