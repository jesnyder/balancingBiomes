//! Resurch library - Academic paper search and management

#![allow(dead_code)] // Library code - not all items used internally

pub mod cli;
pub mod db;
pub mod export;
pub mod models;
pub mod repos;
pub mod util;
pub mod website;

pub use db::Database;
pub use models::Paper;
