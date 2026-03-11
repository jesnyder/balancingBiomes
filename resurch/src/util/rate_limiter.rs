//! Rate limiting for API requests

use std::time::{Duration, Instant};
use tokio::sync::Mutex;

/// A simple rate limiter that ensures minimum delay between requests
pub struct RateLimiter {
    min_delay: Duration,
    last_request: Mutex<Option<Instant>>,
}

impl RateLimiter {
    /// Create a new rate limiter with the specified minimum delay between requests
    pub fn new(min_delay: Duration) -> Self {
        Self {
            min_delay,
            last_request: Mutex::new(None),
        }
    }

    /// Create a rate limiter for Google Scholar (70 second delay)
    pub fn google_scholar() -> Self {
        Self::new(Duration::from_secs(70))
    }

    /// Create a rate limiter for standard APIs (2 second delay)
    pub fn standard_api() -> Self {
        Self::new(Duration::from_secs(2))
    }

    /// Wait until it's safe to make another request
    pub async fn wait(&self) {
        let mut last = self.last_request.lock().await;

        if let Some(last_time) = *last {
            let elapsed = last_time.elapsed();
            if elapsed < self.min_delay {
                let wait_time = self.min_delay - elapsed;
                tokio::time::sleep(wait_time).await;
            }
        }

        *last = Some(Instant::now());
    }

    /// Get the minimum delay
    pub fn min_delay(&self) -> Duration {
        self.min_delay
    }
}

/// Batch parallelism helper for rate-limited operations
pub struct BatchProcessor {
    batch_size: usize,
    delay_between_batches: Duration,
}

impl BatchProcessor {
    pub fn new(batch_size: usize, delay_between_batches: Duration) -> Self {
        Self {
            batch_size,
            delay_between_batches,
        }
    }

    /// Process items in batches with delays between batches
    pub async fn process<T, F, Fut, R>(&self, items: Vec<T>, processor: F) -> Vec<R>
    where
        F: Fn(T) -> Fut,
        Fut: std::future::Future<Output = R>,
        T: Clone,
    {
        let mut results = Vec::with_capacity(items.len());

        for (i, chunk) in items.chunks(self.batch_size).enumerate() {
            if i > 0 {
                tokio::time::sleep(self.delay_between_batches).await;
            }

            for item in chunk {
                // Process items sequentially within a batch to respect rate limits
                results.push(processor(item.clone()).await);
            }
        }

        results
    }
}

impl Clone for BatchProcessor {
    fn clone(&self) -> Self {
        Self {
            batch_size: self.batch_size,
            delay_between_batches: self.delay_between_batches,
        }
    }
}
