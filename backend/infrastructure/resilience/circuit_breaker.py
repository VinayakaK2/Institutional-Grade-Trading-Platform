"""
Circuit Breaker
Prevents cascading failures when a downstream dependency is unhealthy.
"""
import time
from enum import Enum
from typing import Callable, Any, TypeVar
from functools import wraps
from backend.core.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T")

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation, requests pass
    OPEN = "open"           # Tripped, requests fail immediately
    HALF_OPEN = "half_open" # Testing if the downstream has recovered

class CircuitBreakerException(Exception):
    """Raised when the circuit is open."""
    pass

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        
    @property
    def state(self) -> CircuitState:
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info(f"CircuitBreaker {self.name} transitioned to HALF_OPEN")
        return self._state

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info(f"CircuitBreaker {self.name} transitioned to CLOSED")
        self._failure_count = 0
        
    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN or self._failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                self._state = CircuitState.OPEN
                logger.warning(f"CircuitBreaker {self.name} tripped to OPEN")

def with_circuit_breaker(breaker: CircuitBreaker) -> Callable:
    """Decorator to wrap async function with a circuit breaker."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if breaker.state == CircuitState.OPEN:
                raise CircuitBreakerException(f"CircuitBreaker {breaker.name} is OPEN")
                
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                # If we don't catch CircuitBreakerException, don't record it as a dependency failure
                if not isinstance(e, CircuitBreakerException):
                    breaker.record_failure()
                raise
        return wrapper
    return decorator
