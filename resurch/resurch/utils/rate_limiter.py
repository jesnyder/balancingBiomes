"""Rate limiting utilities for API requests."""

import asyncio
import time
from typing import Dict, Optional


class RateLimiter:
    """Simple rate limiter that enforces minimum delay between requests."""

    def __init__(self, min_delay: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            min_delay: Minimum delay in seconds between requests
        """
        self.min_delay = min_delay
        self._last_request_time: float = 0

    async def wait(self) -> None:
        """Wait until enough time has passed since the last request."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        self._last_request_time = time.monotonic()

    def wait_sync(self) -> None:
        """Synchronous version of wait."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self._last_request_time = time.monotonic()


class MultiRateLimiter:
    """Rate limiter that handles multiple domains/APIs with different limits."""

    def __init__(self, default_delay: float = 1.0):
        """
        Initialize multi-rate limiter.

        Args:
            default_delay: Default delay for unknown domains
        """
        self.default_delay = default_delay
        self._limiters: Dict[str, RateLimiter] = {}
        self._delays: Dict[str, float] = {}

    def set_delay(self, name: str, delay: float) -> None:
        """Set the delay for a specific name/domain."""
        self._delays[name] = delay
        if name in self._limiters:
            self._limiters[name].min_delay = delay

    def get_limiter(self, name: str) -> RateLimiter:
        """Get or create a rate limiter for a specific name."""
        if name not in self._limiters:
            delay = self._delays.get(name, self.default_delay)
            self._limiters[name] = RateLimiter(delay)
        return self._limiters[name]

    async def wait(self, name: str) -> None:
        """Wait for the rate limiter associated with the given name."""
        await self.get_limiter(name).wait()

    def wait_sync(self, name: str) -> None:
        """Synchronous wait for the rate limiter associated with the given name."""
        self.get_limiter(name).wait_sync()


# Global rate limiter instance
_global_limiter: Optional[MultiRateLimiter] = None


def get_global_limiter() -> MultiRateLimiter:
    """Get the global rate limiter, creating it if needed."""
    global _global_limiter
    if _global_limiter is None:
        from ..config import RATE_LIMITS
        _global_limiter = MultiRateLimiter()
        for name, delay in RATE_LIMITS.items():
            _global_limiter.set_delay(name, delay)
    return _global_limiter
