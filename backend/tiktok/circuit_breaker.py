import asyncio
import enum
import time
from dataclasses import dataclass, field


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Per-account circuit breaker with proper async locking.

    - CLOSED: Normal operation. Counts failures.
    - OPEN: All requests fail-fast. Transitions to HALF_OPEN after recovery_timeout.
    - HALF_OPEN: Allows exactly one probe request. Success -> CLOSED, failure -> OPEN.
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds
    window: float = 60.0  # failure counting window

    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failures: list[float] = field(default_factory=list, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _probe_in_progress: bool = field(default=False, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    async def record_success(self) -> None:
        async with self._lock:
            self._failures.clear()
            self._state = CircuitState.CLOSED
            self._probe_in_progress = False

    async def record_failure(self) -> None:
        async with self._lock:
            now = time.time()
            self._failures = [t for t in self._failures if now - t < self.window]
            self._failures.append(now)
            self._last_failure_time = now
            self._probe_in_progress = False

            if len(self._failures) >= self.failure_threshold:
                self._state = CircuitState.OPEN

    async def allow_request(self) -> bool:
        async with self._lock:
            state = self.state
            if state == CircuitState.CLOSED:
                return True
            if state == CircuitState.HALF_OPEN:
                # Only allow one probe request at a time
                if not self._probe_in_progress:
                    self._probe_in_progress = True
                    return True
                return False
            return False


class CircuitBreakerRegistry:
    """Per-(platform, account) circuit breaker registry.

    Isolates circuit breaker state per account to prevent one bad tenant
    from tripping the breaker for all other tenants on the same platform.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        window: float = 60.0,
    ) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._window = window

    def get(self, platform: str, account_id: str) -> CircuitBreaker:
        key = f"{platform}:{account_id}"
        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(
                failure_threshold=self._failure_threshold,
                recovery_timeout=self._recovery_timeout,
                window=self._window,
            )
        return self._breakers[key]


# Global registry — each (platform, account) gets its own breaker
circuit_breaker_registry = CircuitBreakerRegistry()


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is in OPEN state."""
