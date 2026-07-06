"""
Mock Historical Provider for Testing
"""
from typing import AsyncGenerator
import asyncio
from datetime import datetime, timedelta
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.models.raw import RawCandle
from backend.historical_data.providers.base import BaseHistoricalProvider
from backend.historical_data.exceptions import ProviderUnavailableException, RateLimitException

class MockHistoricalProvider(BaseHistoricalProvider):
    """
    In-memory provider strictly for testing pipelines and failover logic.
    """
    def __init__(self, name: str = "mock_provider", healthy: bool = True, force_rate_limit: bool = False):
        self._name = name
        self._healthy = healthy
        self._force_rate_limit = force_rate_limit
        
    @property
    def name(self) -> str:
        return self._name
        
    def _supported_timeframes(self) -> set:
        return {Timeframe.M1, Timeframe.M5, Timeframe.H1, Timeframe.D1}
        
    async def is_healthy(self) -> bool:
        return self._healthy
        
    async def get_historical_data(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> AsyncGenerator[RawCandle, None]:
        
        if not self.supports_timeframe(timeframe):
            from backend.historical_data.exceptions import InvalidTimeframeException
            raise InvalidTimeframeException(timeframe.value, self.name)
        if not self._healthy:
            raise ProviderUnavailableException(self.name, "Mock provider is configured as unhealthy")
            
        if self._force_rate_limit:
            raise RateLimitException(self.name, 60)
            
        current = start
        increment = timedelta(minutes=timeframe.to_minutes())
        
        # Simulate network delay for first chunk
        await asyncio.sleep(0.01)
        
        base_price = 100.0
        while current <= end:
            yield RawCandle(
                provider=self.name,
                symbol=symbol,
                timeframe=timeframe,
                raw_timestamp=current.isoformat(),
                raw_open=base_price,
                raw_high=base_price + 1.0,
                raw_low=base_price - 1.0,
                raw_close=base_price + 0.5,
                raw_volume=1000.0
            )
            current += increment
            base_price += 0.1
