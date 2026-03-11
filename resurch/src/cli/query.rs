//! Query subcommand implementation

use crate::cli::args::QueryArgs;
use crate::db::Database;
use anyhow::{Context, Result};
use rusqlite::types::ValueRef;

/// Run the query subcommand
pub async fn run(args: QueryArgs) -> Result<()> {
    let db = Database::open_default()?;
    execute_query(&db, &args.sql, &args.output)
}

/// Execute SQL query and display results
fn execute_query(db: &Database, sql: &str, output: &str) -> Result<()> {
    let conn = db.conn();
    let mut stmt = conn.prepare(sql).context("Invalid SQL query")?;

    // Get column names
    let column_names: Vec<String> = stmt.column_names().iter().map(|s| s.to_string()).collect();
    let column_count = column_names.len();

    // Execute query and collect rows
    let mut rows_data: Vec<Vec<String>> = Vec::new();

    let rows = stmt.query_map([], |row| {
        let mut values = Vec::with_capacity(column_count);
        for i in 0..column_count {
            let value = match row.get_ref(i)? {
                ValueRef::Null => "NULL".to_string(),
                ValueRef::Integer(i) => i.to_string(),
                ValueRef::Real(f) => f.to_string(),
                ValueRef::Text(s) => String::from_utf8_lossy(s).to_string(),
                ValueRef::Blob(b) => format!("<blob {} bytes>", b.len()),
            };
            values.push(value);
        }
        Ok(values)
    })?;

    for row in rows {
        rows_data.push(row?);
    }

    // Record query in history
    conn.execute(
        "INSERT INTO query_history (query_text, result_count) VALUES (?1, ?2)",
        rusqlite::params![sql, rows_data.len()],
    )
    .ok();

    // Output results
    match output {
        "json" => output_json(&column_names, &rows_data),
        "csv" => output_csv(&column_names, &rows_data),
        _ => output_table(&column_names, &rows_data),
    }
}

/// Output as a formatted table
fn output_table(columns: &[String], rows: &[Vec<String>]) -> Result<()> {
    if rows.is_empty() {
        println!("No results.");
        return Ok(());
    }

    // Calculate column widths
    let mut widths: Vec<usize> = columns.iter().map(|c| c.len()).collect();
    for row in rows {
        for (i, value) in row.iter().enumerate() {
            widths[i] = widths[i].max(value.len().min(50)); // Cap at 50 chars
        }
    }

    // Print header
    let header: Vec<String> = columns
        .iter()
        .zip(&widths)
        .map(|(c, w)| format!("{:width$}", c, width = *w))
        .collect();
    println!("{}", header.join(" | "));
    println!(
        "{}",
        widths
            .iter()
            .map(|w| "-".repeat(*w))
            .collect::<Vec<_>>()
            .join("-+-")
    );

    // Print rows
    for row in rows {
        let formatted: Vec<String> = row
            .iter()
            .zip(&widths)
            .map(|(v, w)| {
                let truncated: String = v.chars().take(*w).collect();
                format!("{:width$}", truncated, width = *w)
            })
            .collect();
        println!("{}", formatted.join(" | "));
    }

    println!("\n{} row(s)", rows.len());

    Ok(())
}

/// Output as JSON
fn output_json(columns: &[String], rows: &[Vec<String>]) -> Result<()> {
    let json_rows: Vec<serde_json::Value> = rows
        .iter()
        .map(|row| {
            let obj: serde_json::Map<String, serde_json::Value> = columns
                .iter()
                .zip(row)
                .map(|(k, v)| (k.clone(), serde_json::Value::String(v.clone())))
                .collect();
            serde_json::Value::Object(obj)
        })
        .collect();

    println!("{}", serde_json::to_string_pretty(&json_rows)?);
    Ok(())
}

/// Output as CSV
fn output_csv(columns: &[String], rows: &[Vec<String>]) -> Result<()> {
    let mut writer = csv::Writer::from_writer(std::io::stdout());
    writer.write_record(columns)?;
    for row in rows {
        writer.write_record(row)?;
    }
    writer.flush()?;
    Ok(())
}
