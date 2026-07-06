import pytest
from datetime import date
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.detectors.gaps import GapDetector
from backend.data_validation.contracts.rule import ValidationContext

class DummyMarketTimeService:
    async def is_trading_day(self, exchange_code: str, target_date: date) -> bool:
        # Weekend logic
        if target_date.weekday() >= 5:
            return False
        # Specific holiday simulation
        if target_date == date(2024, 1, 15):
            return False
        return True

@pytest.fixture
def base_context():
    return ValidationContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        provider="test_provider",
        dependencies={"market_time_service": DummyMarketTimeService()}
    )

@pytest.mark.asyncio
async def test_gap_detector_no_gap(base_context):
    rule = GapDetector()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z", # Monday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        ),
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-02T00:00:00Z", # Tuesday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_gap_detector_weekend_gap_ignored(base_context):
    rule = GapDetector()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-05T00:00:00Z", # Friday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        ),
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-08T00:00:00Z", # Monday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        )
    ]
    results = await rule.validate(base_context, records)
    # The gap was a weekend, so no missing trading days
    assert len(results) == 0

@pytest.mark.asyncio
async def test_gap_detector_missing_trading_day(base_context):
    rule = GapDetector()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z", # Monday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        ),
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-03T00:00:00Z", # Wednesday
            raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "Missing 1 trading days" in results[0].message

@pytest.mark.asyncio
async def test_gap_detector_missing_dependency(base_context):
    rule = GapDetector()
    base_context.dependencies = {} # Remove dependency
    records = [
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="2024-01-01T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100),
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="2024-01-03T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100)
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_gap_detector_missing_multiple_days(base_context):
    rule = GapDetector()
    records = [
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="2024-01-01T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100),
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="2024-01-04T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100)
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "Missing 2 trading days" in results[0].message

@pytest.mark.asyncio
async def test_gap_detector_bad_timestamp(base_context):
    rule = GapDetector()
    records = [
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="INVALID_DATE", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100),
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="2024-01-04T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=100)
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0
