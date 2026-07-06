"""
Market Data Access Service
Provides a clean API for application modules to fetch market data, completely hiding provider complexity.
"""
from typing import List, Optional
from datetime import datetime
from backend.market_data.provider.manager import ProviderManager
from backend.market_data.provider.interface import BaseProvider
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.infrastructure.cache.manager import CacheManager
from backend.core.logger import get_logger

logger = get_logger(__name__)

class MarketDataAccessService:
    """Service layer for fetching market data across providers with caching."""
    
    def __init__(self, provider_manager: ProviderManager, cache_manager: CacheManager):
        self._manager = provider_manager
        self._cache = cache_manager

    async def get_latest_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        count: int = 100
    ) -> List[Candle]:
        """
        Retrieves the latest candles, utilizing cache if available, 
        and failing over between providers if necessary.
        """
        # Note: Live latest candles might not be fully cacheable for long, 
        # but for demonstration we can cache them briefly (e.g. 5 seconds)
        # to prevent hammering APIs on multi-strategy reads.
        
        cache_id = f"{timeframe.value}:latest:{count}"
        cached = await self._cache.get("market_data", symbol.full_name, cache_id)
        if cached:
            logger.debug(f"Cache hit for latest candles: {symbol.full_name} {timeframe}")
            return [Candle(**c) for c in cached]

        async def fetch_operation(provider: BaseProvider) -> List[Candle]:
            return await provider.fetch_latest_candles(symbol, timeframe, count)
            
        candles = await self._manager.execute_with_failover(
            fetch_operation, 
            operation_name=f"get_latest_candles({symbol.full_name})"
        )
        
        if candles:
            # Short cache TTL for latest data (e.g. 10 seconds)
            await self._cache.set("market_data", symbol.full_name, cache_id, [c.model_dump() for c in candles], ttl=10)
            
        return candles

    async def get_historical_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start_time: datetime, 
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """
        Retrieves historical candles for a specific date range.
        Historical data is immutable and highly cacheable.
        """
        end_str = end_time.isoformat() if end_time else "now"
        cache_id = f"{timeframe.value}:hist:{start_time.isoformat()}_{end_str}"
        
        cached = await self._cache.get("market_data", symbol.full_name, cache_id)
        if cached:
            logger.debug(f"Cache hit for historical candles: {symbol.full_name} {timeframe}")
            return [Candle(**c) for c in cached]

        async def fetch_operation(provider: BaseProvider) -> List[Candle]:
            return await provider.fetch_historical_candles(symbol, timeframe, start_time, end_time)
            
        candles = await self._manager.execute_with_failover(
            fetch_operation, 
            operation_name=f"get_historical_candles({symbol.full_name})"
        )
        
        if candles:
            # Long cache TTL for historical data (e.g. 1 hour)
            await self._cache.set("market_data", symbol.full_name, cache_id, [c.model_dump() for c in candles], ttl=3600)
            
        return candles
