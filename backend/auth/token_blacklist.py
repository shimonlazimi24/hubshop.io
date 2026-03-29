import redis.asyncio as redis

from backend.config import settings

_redis: redis.Redis | None = None

_KEY_PREFIX = "blacklisted_token:"


async def _get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def blacklist_token(token_jti: str, expires_in: int) -> None:
    """Add a token JTI to the blacklist with a TTL matching the token's remaining life."""
    r = await _get_redis()
    if expires_in > 0:
        await r.setex(f"{_KEY_PREFIX}{token_jti}", expires_in, "1")


async def is_token_blacklisted(token_jti: str) -> bool:
    """Check whether a token JTI has been blacklisted."""
    r = await _get_redis()
    return await r.exists(f"{_KEY_PREFIX}{token_jti}") > 0
