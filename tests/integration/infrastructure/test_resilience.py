"""
Integration Tests for Resilience Framework
"""
import pytest
import asyncio
from backend.infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitState, with_circuit_breaker, CircuitBreakerException
from backend.infrastructure.resilience.retry import async_retry

@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    breaker = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.1)
    
    @with_circuit_breaker(breaker)
    async def failing_func():
        raise ValueError("Fail")
        
    # Attempt 1: Fails, but circuit remains CLOSED
    with pytest.raises(ValueError):
        await failing_func()
    assert breaker.state == CircuitState.CLOSED
    
    # Attempt 2: Fails, threshold reached, trips to OPEN
    with pytest.raises(ValueError):
        await failing_func()
    assert breaker.state == CircuitState.OPEN
    
    # Attempt 3: Immediately fails due to OPEN circuit (raises CircuitBreakerException)
    with pytest.raises(CircuitBreakerException):
        await failing_func()
        
    # Wait for recovery timeout
    await asyncio.sleep(0.15)
    
    # State should now be HALF_OPEN
    assert breaker.state == CircuitState.HALF_OPEN

@pytest.mark.asyncio
async def test_async_retry():
    attempts = 0
    
    @async_retry(max_retries=2, base_delay=0.01)
    async def retry_func():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Temporary Fail")
        return "Success"
        
    result = await retry_func()
    
    assert result == "Success"
    assert attempts == 3
