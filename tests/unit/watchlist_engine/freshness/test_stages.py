import pytest
import datetime
from unittest.mock import AsyncMock

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistSymbol, WatchlistExecutionContext
from backend.watchlist_engine.freshness.config import FreshnessSettings
from backend.watchlist_engine.freshness.stages import (
    FreshnessValidationStage,
    AvailabilityValidationStage,
    DatasetIntegrityValidationStage
)

@pytest.fixture
def candidate_symbol():
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")),
            market_segment="US",
            is_certified=True
        ),
        metadata={}
    )

@pytest.fixture
def context(candidate_symbol):
    now = datetime.datetime.now(datetime.timezone.utc)
    ctx = WatchlistExecutionContext(
        run_id="test_run",
        snapshot_id="test_snapshot",
        started_at=now,
        candidates=[candidate_symbol],
        shared_state={"dataset_version": "v1.0.0"}
    )
    return ctx

@pytest.mark.asyncio
async def test_freshness_validation_stage_accepts_fresh_data(context, candidate_symbol):
    settings = FreshnessSettings(max_data_age_days=3)
    candle_query = AsyncMock()
    market_time = AsyncMock()
    
    # Mock a fresh candle
    now = datetime.datetime.now(datetime.timezone.utc)
    fresh_candle = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")),
        timeframe=Timeframe.D1.value,
        timestamp=now,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1000,
        is_closed=True
    )
    candle_query.get_latest_candles.return_value = [fresh_candle]
    
    stage = FreshnessValidationStage(settings, candle_query, market_time)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 1
    assert context.candidates[0] == candidate_symbol
    candle_query.get_latest_candles.assert_called_once_with(candidate_symbol.watchlist_symbol.symbol, Timeframe.D1, 1)

@pytest.mark.asyncio
async def test_freshness_validation_stage_rejects_stale_data(context, candidate_symbol):
    settings = FreshnessSettings(max_data_age_days=3)
    candle_query = AsyncMock()
    market_time = AsyncMock()
    
    # Mock a stale candle (4 days old)
    stale = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=4)
    stale_candle = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")),
        timeframe=Timeframe.D1.value,
        timestamp=stale,
        open=100.0, high=110.0, low=90.0, close=105.0, volume=1000, is_closed=True
    )
    candle_query.get_latest_candles.return_value = [stale_candle]
    
    stage = FreshnessValidationStage(settings, candle_query, market_time)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 0
    assert result.metadata["rejected_count"] == 1
    assert len(result.warnings) == 1

@pytest.mark.asyncio
async def test_availability_validation_stage_accepts_matching_version(context, candidate_symbol):
    dataset_query = AsyncMock()
    dataset_query.get_canonical_dataset_version.return_value = "v1.0.0"
    
    stage = AvailabilityValidationStage(dataset_query)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 1

@pytest.mark.asyncio
async def test_availability_validation_stage_rejects_mismatching_version(context, candidate_symbol):
    dataset_query = AsyncMock()
    dataset_query.get_canonical_dataset_version.return_value = "v0.9.0"
    
    stage = AvailabilityValidationStage(dataset_query)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 0
    assert result.metadata["rejected_count"] == 1

@pytest.mark.asyncio
async def test_dataset_integrity_validation_stage_accepts_monotonic(context, candidate_symbol):
    settings = FreshnessSettings(integrity_check_lookback=2)
    candle_query = AsyncMock()
    
    now = datetime.datetime.now(datetime.timezone.utc)
    older = now - datetime.timedelta(days=1)
    
    older_candle = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")), timeframe=Timeframe.D1.value, timestamp=older,
        open=100.0, high=110.0, low=90.0, close=105.0, volume=1000, is_closed=True
    )
    newer_candle = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")), timeframe=Timeframe.D1.value, timestamp=now,
        open=100.0, high=110.0, low=90.0, close=105.0, volume=1000, is_closed=True
    )
    
    # Must be in strictly increasing order (or whatever order the query returns, 
    # but the logic assumes [oldest, ..., newest] from the service)
    candle_query.get_latest_candles.return_value = [older_candle, newer_candle]
    
    stage = DatasetIntegrityValidationStage(settings, candle_query)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 1

@pytest.mark.asyncio
async def test_dataset_integrity_validation_stage_rejects_duplicates(context, candidate_symbol):
    settings = FreshnessSettings(integrity_check_lookback=2)
    candle_query = AsyncMock()
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    candle1 = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")), timeframe=Timeframe.D1.value, timestamp=now,
        open=100.0, high=110.0, low=90.0, close=105.0, volume=1000, is_closed=True
    )
    candle2 = Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")), timeframe=Timeframe.D1.value, timestamp=now,
        open=100.0, high=110.0, low=90.0, close=105.0, volume=1000, is_closed=True
    )
    
    candle_query.get_latest_candles.return_value = [candle1, candle2]
    
    stage = DatasetIntegrityValidationStage(settings, candle_query)
    result = await stage.execute(context)
    
    assert result.status == "SUCCESS"
    assert len(context.candidates) == 0
    assert result.metadata["rejected_count"] == 1
