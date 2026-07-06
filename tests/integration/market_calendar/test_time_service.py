"""
Tests for Market Time Service
"""
import pytest
from datetime import datetime, date
from backend.market_calendar.service.time_service import MarketTimeService
from backend.market_calendar.provider.manager import CalendarProviderManager
from backend.market_calendar.provider.registry import CalendarProviderRegistry
from backend.market_calendar.provider.static_provider import StaticCalendarProvider
from backend.market_calendar.models.session import SessionType
from backend.infrastructure.cache.manager import CacheManager
from backend.market_calendar.config.settings import market_calendar_settings

# Mock minimal Cache Provider
class MockCacheProvider:
    def __init__(self):
        self.store = {}
    async def get(self, key: str):
        return self.store.get(key)
    async def set(self, key: str, value, ttl_seconds=3600):
        self.store[key] = value
    async def delete(self, key: str):
        self.store.pop(key, None)

@pytest.fixture
def time_service():
    registry = CalendarProviderRegistry()
    registry.register(StaticCalendarProvider())
    market_calendar_settings.primary_provider = "static_calendar"
    
    manager = CalendarProviderManager(registry=registry)
    cache = CacheManager(provider=MockCacheProvider())
    return MarketTimeService(provider_manager=manager, cache_manager=cache)

@pytest.mark.asyncio
async def test_is_trading_day(time_service):
    # Jan 1st 2025 is a Wednesday, but hardcoded as holiday in StaticProvider
    is_trading = await time_service.is_trading_day("NSE", date(2025, 1, 1))
    assert is_trading is False
    
    # Jan 2nd 2025 is a Thursday (Trading Day)
    is_trading = await time_service.is_trading_day("NSE", date(2025, 1, 2))
    assert is_trading is True
    
    # Jan 4th 2025 is a Saturday
    is_trading = await time_service.is_trading_day("NSE", date(2025, 1, 4))
    assert is_trading is False

@pytest.mark.asyncio
async def test_get_current_session(time_service):
    # Jan 2nd 2025, 10:00 AM IST (04:30 AM UTC) -> Normal Session
    utc_time_normal = datetime(2025, 1, 2, 4, 30, 0)
    session_type, _ = await time_service.get_current_session("NSE", utc_time_normal)
    assert session_type == SessionType.NORMAL
    
    # Jan 2nd 2025, 03:30 AM UTC (09:00 AM IST) -> Pre-Market
    utc_time_pre = datetime(2025, 1, 2, 3, 30, 0)
    session_type, _ = await time_service.get_current_session("NSE", utc_time_pre)
    assert session_type == SessionType.PRE_MARKET
    
    # Weekend
    utc_time_weekend = datetime(2025, 1, 4, 4, 30, 0)
    session_type, _ = await time_service.get_current_session("NSE", utc_time_weekend)
    assert session_type == SessionType.CLOSED

@pytest.mark.asyncio
async def test_is_market_open(time_service):
    utc_time_normal = datetime(2025, 1, 2, 4, 30, 0)
    is_open = await time_service.is_market_open("NSE", utc_time_normal)
    assert is_open is True

@pytest.mark.asyncio
async def test_get_next_trading_day(time_service):
    # Friday Jan 3rd 2025 -> Next should be Monday Jan 6th 2025
    next_day = await time_service.get_next_trading_day("NSE", date(2025, 1, 3))
    assert next_day == date(2025, 1, 6)
