import enum
import time
from dataclasses import dataclass, field


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Per-platform circuit breaker.

    - CLOSED: Normal operation. Counts failures.
    - OPEN: All requests fail-fast. Transitions to HALF_OPEN after recovery_timeout.
    - HALF_OPEN: Allows one probe request. Success -> CLOSED, failure -> OPEN.
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds
    window: float = 60.0  # failure counting window

    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failures: list[float] = field(default_factory=list, init=False)
    _last_failure_time: float = field(default=0.0, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def record_success(self) -> None:
        self._failures.clear()
        self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        now = time.time()
        self._failures = [t for t in self._failures if now - t < self.window]
        self._failures.append(now)
        self._last_failure_time = now

        if len(self._failures) >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def allow_request(self) -> bool:
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            return True  # Allow probe request
        return False


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is in OPEN state."""
