"""
Historical Storage Contract
"""
from typing import List, Protocol, runtime_checkable, AsyncGenerator
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.models.metadata import DownloadMetadata
from datetime import datetime

@runtime_checkable
class HistoricalStorageContract(Protocol):
    """
    Interface for the data persistence layer.
    """
    
    async def save_raw_candles(self, candles: List[RawCandle]) -> None:
        """Saves immutable raw footprint from providers idempotently."""
        ...
        
    async def save_normalized_candles(self, candles: List[Candle]) -> None:
        """Saves canonical, validated candles idempotently."""
        ...
        
    async def get_raw_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> AsyncGenerator[RawCandle, None]:
        """Fetches raw candles for replay/re-normalization."""
        ...
        
    async def save_metadata(self, metadata: DownloadMetadata) -> None:
        """Persists download execution state and metrics."""
        ...
