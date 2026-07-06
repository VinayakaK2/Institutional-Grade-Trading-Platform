"""
Normalization Framework Interface
"""
from typing import Protocol, List, Any
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class BaseNormalizer(Protocol):
    """
    Abstract protocol that every market data provider must implement.
    Responsible for converting raw proprietary JSON into our universal Candle model.
    """
    
    def normalize_candles(
        self, 
        raw_data: Any, 
        symbol: SymbolReference, 
        timeframe: Timeframe
    ) -> List[Candle]:
        """
        Takes raw provider data and returns a sorted list of standard Candles.
        Must raise DataNormalizationException if the raw_data is corrupted or missing required fields.
        """
        ...
