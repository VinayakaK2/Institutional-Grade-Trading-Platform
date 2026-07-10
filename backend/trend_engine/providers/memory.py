"""
Trend Engine InMemory Providers
===============================

Mock/In-Memory providers for Indicators and Market Structure.
Used strictly for testing and validation of the Trend Engine isolation.
"""
from typing import List, Dict

from backend.trend_engine.contracts.contracts import IIndicatorProvider, IStructureProvider
from backend.market_data.models.symbol import SymbolReference
from backend.indicator_engine.models.indicator import IndicatorResult
from backend.market_structure_engine.models.structure import MarketStructurePoint


class InMemoryIndicatorProvider(IIndicatorProvider):
    """
    In-memory provider for testing EMA detection.
    Pre-load with `seed_data` dictionary keyed by symbol string.
    """
    def __init__(self, seed_data: Dict[str, Dict[int, IndicatorResult]] = None):
        self._data = seed_data or {}
        
    async def get_ema_indicators(
        self, 
        symbol: SymbolReference, 
        snapshot_id: str,
        periods: List[int]
    ) -> Dict[int, IndicatorResult]:
        symbol_key = f"{symbol.symbol}:{symbol.exchange.code}"
        if symbol_key not in self._data:
            return {}
            
        result = {}
        for p in periods:
            if p in self._data[symbol_key]:
                result[p] = self._data[symbol_key][p]
                
        return result


class InMemoryStructureProvider(IStructureProvider):
    """
    In-memory provider for testing Price Structure detection.
    Pre-load with `seed_data` dictionary keyed by symbol string.
    """
    def __init__(self, seed_data: Dict[str, List[MarketStructurePoint]] = None):
        self._data = seed_data or {}
        
    async def get_latest_structures(
        self, 
        symbol: SymbolReference, 
        snapshot_id: str,
        limit: int = 2
    ) -> List[MarketStructurePoint]:
        symbol_key = f"{symbol.symbol}:{symbol.exchange.code}"
        if symbol_key not in self._data:
            return []
            
        return self._data[symbol_key][:limit]
