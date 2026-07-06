"""
Historical Provider Contract
"""
from typing import AsyncGenerator, Protocol, runtime_checkable
from datetime import datetime
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.models.raw import RawCandle

@runtime_checkable
class HistoricalProviderContract(Protocol):
    """
    Interface for all historical data providers.
    Switching providers must require ZERO application changes.
    """
    
    @property
    def name(self) -> str:
        """The unique identifier name of the provider."""
        ...
        
    def get_historical_data(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> AsyncGenerator[RawCandle, None]:
        """
        Fetches historical data for the given symbol and timeframe.
        Must yield RawCandle objects, representing the unmodified provider response.
        """
        ...
        
    async def is_healthy(self) -> bool:
        """Returns True if the provider is currently reachable and operational."""
        ...
        
    def supports_timeframe(self, timeframe: Timeframe) -> bool:
        """Returns True if the provider supports the requested timeframe."""
        ...
