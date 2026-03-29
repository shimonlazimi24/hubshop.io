"""Tests for SecurityHeadersMiddleware (backend/main.py)."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.config import settings
from backend.main import create_app


@pytest.mark.unit
class TestSecurityHeadersMiddleware:
    """Verify security headers are present on all responses."""

    async def test_x_content_type_options_header(self) -> None:
        """Response should include X-Content-Type-Options: nosniff."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    async def test_x_frame_options_header(self) -> None:
        """Response should include X-Frame-Options: DENY."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert resp.headers.get("X-Frame-Options") == "DENY"

    async def test_referrer_policy_header(self) -> None:
        """Response should include Referrer-Policy header."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    async def test_xss_protection_header(self) -> None:
        """Response should include X-XSS-Protection header."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert resp.headers.get("X-XSS-Protection") == "1; mode=block"

    async def test_permissions_policy_header(self) -> None:
        """Response should include Permissions-Policy header."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert "camera=()" in resp.headers.get("Permissions-Policy", "")

    async def test_hsts_absent_in_debug_mode(self) -> None:
        """HSTS header should NOT be present when debug=True (default test env)."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert "Strict-Transport-Security" not in resp.headers

    async def test_hsts_present_when_debug_false(self) -> None:
        """HSTS header should be present when debug=False (production-like)."""
        app = create_app()
        original_debug = settings.debug
        try:
            # Temporarily set debug to False on the real settings object
            # so the middleware dispatch method reads it at request time.
            object.__setattr__(settings, "debug", False)
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/health")

            hsts = resp.headers.get("Strict-Transport-Security", "")
            assert "max-age=" in hsts
        finally:
            object.__setattr__(settings, "debug", original_debug)
