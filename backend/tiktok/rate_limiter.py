import time

import redis.asyncio as redis

from backend.config import settings

_redis: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


class TokenBucketRateLimiter:
    """Redis-backed token bucket rate limiter.

    Each platform + account combination gets its own bucket.
    """

    def __init__(self, max_tokens: int, refill_rate: float, key_prefix: str) -> None:
        self._max_tokens = max_tokens
        self._refill_rate = refill_rate  # tokens per second
        self._key_prefix = key_prefix

    async def acquire(self, account_id: str) -> bool:
        """Try to acquire a token. Returns True if allowed, False if rate limited."""
        r = await get_redis()
        key = f"rate_limit:{self._key_prefix}:{account_id}"
        now = time.time()

        pipe = r.pipeline()
        pipe.hmget(key, "tokens", "last_refill")
        results = await pipe.execute()
        stored = results[0]

        tokens = float(stored[0]) if stored[0] else float(self._max_tokens)
        last_refill = float(stored[1]) if stored[1] else now

        # Refill tokens
        elapsed = now - last_refill
        tokens = min(self._max_tokens, tokens + elapsed * self._refill_rate)

        if tokens < 1.0:
            return False

        tokens -= 1.0
        pipe2 = r.pipeline()
        pipe2.hset(key, mapping={"tokens": str(tokens), "last_refill": str(now)})
        pipe2.expire(key, 120)  # Auto-cleanup after 2 min idle
        await pipe2.execute()
        return True


# Pre-configured rate limiters per platform
shop_rate_limiter = TokenBucketRateLimiter(
    max_tokens=50, refill_rate=50.0, key_prefix="shop"  # 50 QPS
)
developer_rate_limiter = TokenBucketRateLimiter(
    max_tokens=10, refill_rate=10.0, key_prefix="developer"  # 600/min = 10/s
)
marketing_rate_limiter = TokenBucketRateLimiter(
    max_tokens=10, refill_rate=10.0, key_prefix="marketing"  # Conservative default
)
research_rate_limiter = TokenBucketRateLimiter(
    max_tokens=5, refill_rate=5.0, key_prefix="research"  # Research API: 5 QPS
)
live_rate_limiter = TokenBucketRateLimiter(
    max_tokens=100, refill_rate=100.0, key_prefix="live"  # LIVE has no formal limit
)
