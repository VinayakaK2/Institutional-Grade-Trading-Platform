"""
Base Historical Provider
"""
from typing import AsyncGenerator
from datetime import datetime
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.contracts.provider import HistoricalProviderContract
from backend.historical_data.models.raw import RawCandle
from backend.historical_data.exceptions import InvalidTimeframeException

class BaseHistoricalProvider(HistoricalProviderContract):
    """
    Abstract base provider mapping standard behaviors.
    """
    
    @property
    def name(self) -> str:
        raise NotImplementedError
        
    def _supported_timeframes(self) -> set:
        """Returns the set of Timeframes supported by this provider."""
        raise NotImplementedError
        
    def supports_timeframe(self, timeframe: Timeframe) -> bool:
        return timeframe in self._supported_timeframes()
        
    async def is_healthy(self) -> bool:
        """Default health check implementation. Override if provider requires an API ping."""
        return True
        
    def get_historical_data(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> AsyncGenerator[RawCandle, None]:
        
        if not self.supports_timeframe(timeframe):
            raise InvalidTimeframeException(timeframe.value, self.name)
            
        # Implementation left to the concrete class
        # yield RawCandle(...)
        
        # Pydantic typing requires us to yield something if we use yield in abstract.
        # But wait, Python doesn't need a dummy yield in an abstract method if we just raise NotImplementedError
        raise NotImplementedError
