from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
import threading

class IndicatorCacheContract(ABC):
    @abstractmethod
    def get(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str
    ) -> Optional[List[IndicatorResult]]:
        """Retrieves cached results for a specific indicator series."""
        pass
        
    @abstractmethod
    def set(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str,
        results: List[IndicatorResult]
    ) -> None:
        """Saves results for a specific indicator series."""
        pass

    @abstractmethod
    def invalidate(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str
    ) -> None:
        """Explicitly invalidates a cache entry."""
        pass

class MemoryIndicatorCache(IndicatorCacheContract):
    """
    In-memory thread-safe cache for indicators.
    Invalidation is data-driven by the orchestrator (overwrites).
    """
    def __init__(self):
        self._cache: Dict[str, List[IndicatorResult]] = {}
        self._lock = threading.Lock()
        
    def _generate_key(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str
    ) -> str:
        return f"{symbol.symbol}_{timeframe.value}_{dataset_version}_{indicator_type.value}_{param_key}"

    def get(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str
    ) -> Optional[List[IndicatorResult]]:
        key = self._generate_key(symbol, timeframe, dataset_version, indicator_type, param_key)
        with self._lock:
            return self._cache.get(key)
            
    def set(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str,
        results: List[IndicatorResult]
    ) -> None:
        if not results:
            return
            
        key = self._generate_key(symbol, timeframe, dataset_version, indicator_type, param_key)
        with self._lock:
            # We clone the list to prevent external mutation issues
            self._cache[key] = list(results)

    def invalidate(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        indicator_type: IndicatorType, 
        param_key: str
    ) -> None:
        key = self._generate_key(symbol, timeframe, dataset_version, indicator_type, param_key)
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear_all(self):
        with self._lock:
            self._cache.clear()
