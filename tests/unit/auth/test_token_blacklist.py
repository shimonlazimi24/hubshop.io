"""Tests for the Redis-backed token blacklist (backend/auth/token_blacklist.py)."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.auth.token_blacklist import blacklist_token, is_token_blacklisted


@pytest.mark.unit
class TestBlacklistToken:
    """Tests for blacklist_token()."""

    async def test_stores_key_in_redis_with_ttl(self) -> None:
        """blacklist_token should call setex with the correct key and TTL."""
        mock_redis = AsyncMock()

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            await blacklist_token("test-jti-123", 900)

        mock_redis.setex.assert_awaited_once_with(
            "blacklisted_token:test-jti-123", 900, "1"
        )

    async def test_zero_ttl_does_not_store(self) -> None:
        """blacklist_token with expires_in=0 should not store anything."""
        mock_redis = AsyncMock()

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            await blacklist_token("test-jti-zero", 0)

        mock_redis.setex.assert_not_awaited()

    async def test_negative_ttl_does_not_store(self) -> None:
        """blacklist_token with negative expires_in should not store anything."""
        mock_redis = AsyncMock()

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            await blacklist_token("test-jti-neg", -100)

        mock_redis.setex.assert_not_awaited()


@pytest.mark.unit
class TestIsTokenBlacklisted:
    """Tests for is_token_blacklisted()."""

    async def test_returns_true_for_blacklisted_token(self) -> None:
        """is_token_blacklisted returns True when Redis key exists."""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            result = await is_token_blacklisted("blacklisted-jti")

        assert result is True
        mock_redis.exists.assert_awaited_once_with("blacklisted_token:blacklisted-jti")

    async def test_returns_false_for_non_blacklisted_token(self) -> None:
        """is_token_blacklisted returns False when Redis key does not exist."""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            result = await is_token_blacklisted("clean-jti")

        assert result is False

    async def test_key_prefix_is_correct(self) -> None:
        """Verify the correct key prefix is used for lookups."""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0

        with patch(
            "backend.auth.token_blacklist._get_redis",
            return_value=mock_redis,
        ):
            await is_token_blacklisted("abc-def")

        call_args = mock_redis.exists.call_args[0][0]
        assert call_args.startswith("blacklisted_token:")
        assert call_args == "blacklisted_token:abc-def"
