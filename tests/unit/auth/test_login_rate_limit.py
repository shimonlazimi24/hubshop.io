"""Tests for login rate limiting (backend/auth/routes.py _check_login_rate_limit)."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from backend.auth.routes import _check_login_rate_limit


@pytest.mark.unit
class TestLoginRateLimit:
    """Tests for the per-email login rate limiter."""

    async def test_first_attempt_succeeds(self) -> None:
        """First login attempt should pass without error."""
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1
        mock_redis.expire = AsyncMock()

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            await _check_login_rate_limit("user@example.com")

        mock_redis.incr.assert_awaited_once()
        mock_redis.expire.assert_awaited_once()

    async def test_fifth_attempt_succeeds(self) -> None:
        """Fifth attempt (at the limit) should still succeed."""
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 5

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            # Should not raise
            await _check_login_rate_limit("user@example.com")

    async def test_sixth_attempt_raises_429(self) -> None:
        """Sixth attempt exceeds the limit and should raise 429."""
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 6
        mock_redis.ttl.return_value = 250

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            with pytest.raises(HTTPException) as exc_info:
                await _check_login_rate_limit("user@example.com")

        assert exc_info.value.status_code == 429
        assert "Too many login attempts" in exc_info.value.detail

    async def test_rate_limit_key_uses_lowercase_email(self) -> None:
        """Rate limit key should normalize email to lowercase."""
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1
        mock_redis.expire = AsyncMock()

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            await _check_login_rate_limit("USER@Example.COM")

        call_args = mock_redis.incr.call_args[0][0]
        assert call_args == "login_rate_limit:user@example.com"

    async def test_redis_unavailable_fails_open(self) -> None:
        """If Redis is unavailable, rate limiting should fail-open (allow request)."""
        mock_redis = AsyncMock()
        mock_redis.incr.side_effect = ConnectionError("Redis down")

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            # Should not raise - fail-open behavior
            await _check_login_rate_limit("user@example.com")

    async def test_sets_expire_only_on_first_attempt(self) -> None:
        """TTL should only be set on the first increment (attempts == 1)."""
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 3  # Not first attempt
        mock_redis.expire = AsyncMock()

        with patch("backend.auth.routes._get_redis", return_value=mock_redis):
            await _check_login_rate_limit("user@example.com")

        # expire should NOT be called when attempts > 1
        mock_redis.expire.assert_not_awaited()
