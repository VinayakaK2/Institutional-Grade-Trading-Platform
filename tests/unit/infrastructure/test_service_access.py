import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from backend.market_data.service.access import MarketDataAccessService
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle

@pytest.fixture
def mock_provider_manager():
    return AsyncMock()

@pytest.fixture
def mock_cache_manager():
    return AsyncMock()

@pytest.fixture
def service(mock_provider_manager, mock_cache_manager):
    return MarketDataAccessService(mock_provider_manager, mock_cache_manager)


@pytest.fixture
def sample_candle():
    return Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.H1,
        timestamp=datetime.now(timezone.utc),
        open=100.0, high=105.0, low=95.0, close=102.0, volume=1000.0
    )

@pytest.mark.asyncio
async def test_get_latest_candles_cache_miss(service, mock_provider_manager, mock_cache_manager, sample_candle):
    mock_cache_manager.get.return_value = None
    mock_provider_manager.execute_with_failover.return_value = [sample_candle]
    
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    candles = await service.get_latest_candles(symbol, Timeframe.H1, count=10)
    
    assert len(candles) == 1
    assert candles[0].open == 100.0
    mock_cache_manager.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_historical_candles_cache_miss(service, mock_provider_manager, mock_cache_manager, sample_candle):
    mock_cache_manager.get.return_value = None
    mock_provider_manager.execute_with_failover.return_value = [sample_candle]
    
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    candles = await service.get_historical_candles(symbol, Timeframe.H1, datetime.now(timezone.utc), datetime.now(timezone.utc))
    
    assert len(candles) == 1
    assert candles[0].open == 100.0
    mock_cache_manager.set.assert_called_once()
