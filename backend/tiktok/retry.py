import asyncio
import logging
import random
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


async def with_retry(
    func: Callable[..., Awaitable[T]],
    *args: object,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_total_time: float = 15.0,
    **kwargs: object,
) -> T:
    """Execute an async function with exponential backoff + jitter retry.

    Only retries on 429 (rate limited) and 5xx server errors.
    Adds randomized jitter to prevent thundering herd.
    Enforces a total time limit across all retries.
    """
    last_exception: Exception | None = None
    start_time = time.monotonic()

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                raise
            last_exception = exc
            if attempt < max_retries:
                elapsed = time.monotonic() - start_time
                if elapsed >= max_total_time:
                    logger.warning(
                        "Retry aborted: total time %.1fs exceeds limit %.1fs",
                        elapsed,
                        max_total_time,
                    )
                    break
                # Exponential backoff with jitter (20% randomization)
                delay = base_delay * (2**attempt) * random.uniform(0.8, 1.2)
                logger.warning(
                    "Retry %d/%d after HTTP %d on %s (delay=%.1fs)",
                    attempt + 1,
                    max_retries,
                    exc.response.status_code,
                    str(exc.request.url),
                    delay,
                )
                await asyncio.sleep(delay)
        except httpx.TransportError as exc:
            last_exception = exc
            if attempt < max_retries:
                elapsed = time.monotonic() - start_time
                if elapsed >= max_total_time:
                    logger.warning(
                        "Retry aborted: total time %.1fs exceeds limit %.1fs",
                        elapsed,
                        max_total_time,
                    )
                    break
                delay = base_delay * (2**attempt) * random.uniform(0.8, 1.2)
                logger.warning(
                    "Retry %d/%d after transport error: %s (delay=%.1fs)",
                    attempt + 1,
                    max_retries,
                    str(exc),
                    delay,
                )
                await asyncio.sleep(delay)

    raise last_exception  # type: ignore[misc]
