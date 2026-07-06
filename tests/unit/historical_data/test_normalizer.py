import pytest
from datetime import datetime, timezone
from backend.historical_data.engine.normalizer import DataNormalizer
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.exceptions import NormalizationException

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="AAPL", exchange=ExchangeReference(name="NASDAQ", code="NASDAQ"))

def test_normalize_valid_iso_string(dummy_symbol):
    raw = RawCandle(
        provider="test",
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        raw_timestamp="2024-01-01T00:00:00Z",
        raw_open="150.0",
        raw_high="155.5",
        raw_low="149.0",
        raw_close="152.0",
        raw_volume="1000000"
    )
    candle = DataNormalizer.normalize(raw)
    assert candle.open == 150.0
    assert candle.high == 155.5
    assert candle.timestamp == datetime(2024, 1, 1, tzinfo=timezone.utc)

def test_normalize_invalid_math_raises(dummy_symbol):
    raw = RawCandle(
        provider="test",
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        raw_timestamp="2024-01-01T00:00:00Z",
        raw_open="150.0",
        raw_high="140.0", # High < Open
        raw_low="149.0",
        raw_close="152.0",
        raw_volume="1000000"
    )
    with pytest.raises(NormalizationException):
        DataNormalizer.normalize(raw)

def test_normalize_unix_timestamp(dummy_symbol):
    raw = RawCandle(
        provider="test",
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        raw_timestamp=1704067200, # 2024-01-01T00:00:00
        raw_open="150",
        raw_high="155",
        raw_low="149",
        raw_close="152",
        raw_volume="100"
    )
    candle = DataNormalizer.normalize(raw)
    assert candle.open == 150.0
