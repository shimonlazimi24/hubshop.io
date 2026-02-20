"""Tests for all platforms registered in PlatformGateway."""

from backend.db.models.platform import Platform
from backend.tiktok.gateway import _circuit_breakers, _rate_limiters


class TestGatewayPlatformRegistration:
    def test_all_platforms_have_circuit_breakers(self) -> None:
        for platform in Platform:
            assert platform in _circuit_breakers, f"Missing circuit breaker for {platform}"

    def test_all_platforms_have_rate_limiters(self) -> None:
        for platform in Platform:
            assert platform in _rate_limiters, f"Missing rate limiter for {platform}"

    def test_five_circuit_breakers(self) -> None:
        assert len(_circuit_breakers) == 5

    def test_five_rate_limiters(self) -> None:
        assert len(_rate_limiters) == 5
