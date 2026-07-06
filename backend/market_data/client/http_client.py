"""
Resilient Async HTTP Client for Market Data
"""
import aiohttp
import asyncio
from typing import Any, Dict, Optional
from backend.infrastructure.resilience.retry import async_retry
from backend.infrastructure.resilience.circuit_breaker import CircuitBreaker, with_circuit_breaker, CircuitBreakerException
from backend.market_data.exceptions import ProviderOfflineException, RateLimitExceededException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class MarketDataHttpClient:
    """
    Reusable HTTP Client wrapper designed specifically for Market Data.
    Integrates deeply with our Phase 1.4 Resilience frameworks.
    """
    
    def __init__(self, provider_name: str, circuit_breaker: CircuitBreaker):
        self.provider_name = provider_name
        self._circuit_breaker = circuit_breaker
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None

    # Using async_retry to automatically backoff and retry on transient network errors
    @async_retry(max_retries=3, base_delay=1.0, exceptions=(aiohttp.ClientError, asyncio.TimeoutError))
    async def _safe_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Internal method that executes the request with retry logic."""
        if not self._session:
            raise RuntimeError("Client session is not initialized. Use async with context.")
            
        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    raise RateLimitExceededException(self.provider_name)
                    
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientResponseError as e:
            if e.status >= 500:
                # 5xx errors should trigger a retry (handled by the decorator if we added it, 
                # but currently decorator catches ClientError which is a base class)
                raise
            raise  # 4xx errors usually shouldn't be retried
        except Exception:
            logger.error(f"HTTP Request failed for {self.provider_name}: {url}", exc_info=True)
            raise

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Executes a GET request wrapped in a Circuit Breaker.
        If the provider fails too many times, the circuit trips open, immediately failing subsequent calls.
        """
        @with_circuit_breaker(self._circuit_breaker)
        async def execute_with_cb():
            return await self._safe_request("GET", url, params=params, **kwargs)
            
        try:
            return await execute_with_cb()
        except CircuitBreakerException as e:
            logger.critical(f"Circuit Breaker OPEN for provider {self.provider_name}. Request blocked.")
            raise ProviderOfflineException(self.provider_name, "Circuit breaker tripped.") from e
