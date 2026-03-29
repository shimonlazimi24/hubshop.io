"""Tests for all platforms registered in PlatformGateway."""

from backend.db.models.platform import Platform
from backend.tiktok.circuit_breaker import circuit_breaker_registry
from backend.tiktok.gateway import _rate_limiters


class TestGatewayPlatformRegistration:
    def test_all_platforms_have_rate_limiters(self) -> None:
        for platform in Platform:
            assert platform in _rate_limiters, f"Missing rate limiter for {platform}"

    def test_five_rate_limiters(self) -> None:
        assert len(_rate_limiters) == 5

    def test_circuit_breaker_registry_creates_per_account(self) -> None:
        """Circuit breakers are now per-(platform, account) via the registry."""
        cb1 = circuit_breaker_registry.get("shop", "account_a")
        cb2 = circuit_breaker_registry.get("shop", "account_b")
        assert cb1 is not cb2, (
            "Different accounts should get different circuit breakers"
        )

    def test_circuit_breaker_registry_reuses_same_account(self) -> None:
        cb1 = circuit_breaker_registry.get("shop", "account_x")
        cb2 = circuit_breaker_registry.get("shop", "account_x")
        assert cb1 is cb2, "Same account should get the same circuit breaker instance"
