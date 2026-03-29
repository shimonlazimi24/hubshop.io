import time

import pytest

from backend.tiktok.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitState,
)


@pytest.mark.unit
class TestCircuitBreaker:
    def test_starts_closed(self) -> None:
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_allow_request_when_closed(self) -> None:
        cb = CircuitBreaker()
        assert await cb.allow_request()

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, window=60.0)
        await cb.record_failure()
        await cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        await cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert not await cb.allow_request()

    @pytest.mark.asyncio
    async def test_success_resets_failures(self) -> None:
        cb = CircuitBreaker(failure_threshold=3)
        await cb.record_failure()
        await cb.record_failure()
        await cb.record_success()
        await cb.record_failure()
        # Should still be closed because success cleared the counter
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        await cb.record_failure()
        assert cb.state == CircuitState.OPEN

        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        assert await cb.allow_request()  # Probe allowed

    @pytest.mark.asyncio
    async def test_half_open_blocks_second_probe(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        await cb.record_failure()
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

        assert await cb.allow_request()  # First probe allowed
        assert not await cb.allow_request()  # Second blocked

    @pytest.mark.asyncio
    async def test_half_open_success_closes(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        await cb.record_failure()
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

        await cb.record_success()
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_old_failures_outside_window_ignored(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, window=0.01)
        await cb.record_failure()
        await cb.record_failure()
        time.sleep(0.02)
        await cb.record_failure()
        # Only 1 failure within the window
        assert cb.state == CircuitState.CLOSED


@pytest.mark.unit
class TestCircuitBreakerRegistry:
    def test_creates_per_account(self) -> None:
        registry = CircuitBreakerRegistry()
        cb1 = registry.get("shop", "account_a")
        cb2 = registry.get("shop", "account_b")
        assert cb1 is not cb2

    def test_reuses_same_account(self) -> None:
        registry = CircuitBreakerRegistry()
        cb1 = registry.get("shop", "account_x")
        cb2 = registry.get("shop", "account_x")
        assert cb1 is cb2

    def test_different_platforms_different_breakers(self) -> None:
        registry = CircuitBreakerRegistry()
        cb1 = registry.get("shop", "account_a")
        cb2 = registry.get("marketing", "account_a")
        assert cb1 is not cb2
