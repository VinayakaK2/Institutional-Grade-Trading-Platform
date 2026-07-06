"""
Market Data Provider Interface
"""
from typing import Protocol, List, Optional
from datetime import datetime
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class BaseProvider(Protocol):
    """
    Abstract protocol that every market data provider plugin (e.g., ZerodhaProvider, BinanceProvider) 
    must implement in future phases.
    """
    
    @property
    def name(self) -> str:
        """Unique identifier for the provider."""
        ...
        
    @property
    def is_healthy(self) -> bool:
        """Returns True if the provider's circuit breaker is closed and API is reachable."""
        ...

    async def fetch_latest_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        count: int = 100
    ) -> List[Candle]:
        """Fetches the most recent N candles."""
        ...
        
    async def fetch_historical_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start_time: datetime, 
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """Fetches historical candles for a specific date range."""
        ...
