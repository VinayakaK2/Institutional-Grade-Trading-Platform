"""
Integration Tests for Data Access Service
"""
import pytest
from datetime import datetime
from backend.market_data.service.access import MarketDataAccessService
from backend.market_data.provider.manager import ProviderManager
from backend.market_data.provider.registry import ProviderRegistry
from backend.infrastructure.cache.manager import CacheManager
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.market_data.config.settings import market_data_settings

# Mock cache provider
class MockCacheProvider:
    def __init__(self):
        self.store = {}
    async def get(self, key: str):
        return self.store.get(key)
    async def set(self, key: str, value, ttl_seconds=3600):
        self.store[key] = value
    async def delete(self, key: str):
        self.store.pop(key, None)

class MockSuccessProvider:
    @property
    def name(self): return "mock_success"
    
    @property
    def is_healthy(self): return True
    
    async def fetch_latest_candles(self, symbol, timeframe, count):
        return [
            Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime(2025, 1, 1),
                open=100.0, high=105.0, low=99.0, close=104.0, volume=1000.0
            )
        ]

@pytest.mark.asyncio
async def test_access_service_caching():
    registry = ProviderRegistry()
    registry.register(MockSuccessProvider())
    
    market_data_settings.primary_provider = "mock_success"
    manager = ProviderManager(registry=registry)
    
    cache_provider = MockCacheProvider()
    cache_manager = CacheManager(provider=cache_provider)
    
    service = MarketDataAccessService(manager, cache_manager)
    
    symbol = SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NSE"))
    
    # First call: hits provider, sets cache
    candles = await service.get_latest_candles(symbol, Timeframe.D1, 1)
    assert len(candles) == 1
    assert candles[0].close == 104.0
    
    # Check cache was populated
    cache_key = "market_data:nse:test:1d:latest:1"
    assert cache_provider.store.get(cache_key) is not None
    
    # Second call: hits cache directly
    # We can verify this because even if provider was removed, it still returns data
    registry._providers.clear() 
    candles_cached = await service.get_latest_candles(symbol, Timeframe.D1, 1)
    assert len(candles_cached) == 1
    assert candles_cached[0].close == 104.0
