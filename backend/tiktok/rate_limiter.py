import logging
import time

import redis.asyncio as redis

from backend.config import settings

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None

# Atomic Lua script for token bucket rate limiting.
# Prevents race conditions by doing read-refill-decrement-write in one operation.
_TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or max_tokens
local last_refill = tonumber(data[2]) or now

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
tokens = math.min(max_tokens, tokens + elapsed * refill_rate)

if tokens < 1.0 then
    redis.call('HSET', key, 'tokens', tostring(tokens), 'last_refill', tostring(now))
    redis.call('EXPIRE', key, ttl)
    return 0
end

tokens = tokens - 1.0
redis.call('HSET', key, 'tokens', tostring(tokens), 'last_refill', tostring(now))
redis.call('EXPIRE', key, ttl)
return 1
"""


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


class TokenBucketRateLimiter:
    """Redis-backed token bucket rate limiter.

    Each platform + account combination gets its own bucket.
    Uses an atomic Lua script to prevent race conditions under concurrent load.
    """

    def __init__(self, max_tokens: int, refill_rate: float, key_prefix: str) -> None:
        self._max_tokens = max_tokens
        self._refill_rate = refill_rate  # tokens per second
        self._key_prefix = key_prefix
        self._script_sha: str | None = None

    async def acquire(self, account_id: str) -> bool:
        """Try to acquire a token. Returns True if allowed, False if rate limited.

        Fails open on Redis errors (allows request) to prevent infrastructure
        failures from blocking all API traffic.
        """
        try:
            r = await get_redis()
            key = f"rate_limit:{self._key_prefix}:{account_id}"
            now = time.time()

            # Cache the script SHA to avoid re-sending the script on every call
            if self._script_sha is None:
                self._script_sha = await r.script_load(_TOKEN_BUCKET_SCRIPT)

            result = await r.evalsha(
                self._script_sha,
                1,
                key,
                str(self._max_tokens),
                str(self._refill_rate),
                str(now),
                "120",  # TTL seconds
            )
            return int(result) == 1
        except redis.RedisError:
            logger.warning(
                "Redis error in rate limiter for %s:%s — failing open",
                self._key_prefix,
                account_id,
                exc_info=True,
            )
            # Reset cached script SHA in case Redis restarted
            self._script_sha = None
            return True  # Fail open: allow request when Redis is down


# Pre-configured rate limiters per platform
shop_rate_limiter = TokenBucketRateLimiter(
    max_tokens=50,
    refill_rate=50.0,
    key_prefix="shop",  # 50 QPS
)
developer_rate_limiter = TokenBucketRateLimiter(
    max_tokens=10,
    refill_rate=10.0,
    key_prefix="developer",  # 600/min = 10/s
)
marketing_rate_limiter = TokenBucketRateLimiter(
    max_tokens=10,
    refill_rate=10.0,
    key_prefix="marketing",  # Conservative default
)
research_rate_limiter = TokenBucketRateLimiter(
    max_tokens=5,
    refill_rate=5.0,
    key_prefix="research",  # Research API: 5 QPS
)
live_rate_limiter = TokenBucketRateLimiter(
    max_tokens=100,
    refill_rate=100.0,
    key_prefix="live",  # LIVE has no formal limit
)
