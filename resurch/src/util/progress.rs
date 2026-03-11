//! Progress reporting utilities

use indicatif::{ProgressBar, ProgressStyle};

/// Progress reporter for long-running operations
pub struct ProgressReporter {
    bar: ProgressBar,
}

impl ProgressReporter {
    /// Create a new progress reporter with a known total
    pub fn new(total: u64, message: &str) -> Self {
        let bar = ProgressBar::new(total);
        bar.set_style(
            ProgressStyle::default_bar()
                .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({percent}%) {msg}")
                .expect("Invalid progress bar template")
                .progress_chars("#>-"),
        );
        bar.set_message(message.to_string());
        Self { bar }
    }

    /// Create a spinner for unknown-length operations
    pub fn spinner(message: &str) -> Self {
        let bar = ProgressBar::new_spinner();
        bar.set_style(
            ProgressStyle::default_spinner()
                .template("{spinner:.green} [{elapsed_precise}] {msg}")
                .expect("Invalid spinner template"),
        );
        bar.set_message(message.to_string());
        bar.enable_steady_tick(std::time::Duration::from_millis(100));
        Self { bar }
    }

    /// Increment progress by 1
    pub fn inc(&self) {
        self.bar.inc(1);
    }

    /// Increment progress by a specific amount
    pub fn inc_by(&self, delta: u64) {
        self.bar.inc(delta);
    }

    /// Set the current position
    pub fn set_position(&self, pos: u64) {
        self.bar.set_position(pos);
    }

    /// Update the message
    pub fn set_message(&self, message: &str) {
        self.bar.set_message(message.to_string());
    }

    /// Finish with a message
    pub fn finish(&self, message: &str) {
        self.bar.finish_with_message(message.to_string());
    }

    /// Finish and clear
    pub fn finish_and_clear(&self) {
        self.bar.finish_and_clear();
    }

    /// Abandon the progress bar (for errors/interrupts)
    pub fn abandon(&self, message: &str) {
        self.bar.abandon_with_message(message.to_string());
    }
}

impl Drop for ProgressReporter {
    fn drop(&mut self) {
        if !self.bar.is_finished() {
            self.bar.finish_and_clear();
        }
    }
}
