import pytest
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.validation.rules.ohlcv import OhlcvRule
from backend.data_validation.contracts.rule import ValidationContext

@pytest.fixture
def base_context():
    return ValidationContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        provider="test_provider"
    )

@pytest.mark.asyncio
async def test_ohlcv_rule_valid(base_context):
    rule = OhlcvRule()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100.0,
            raw_high=105.0,
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_ohlcv_rule_invalid_high(base_context):
    rule = OhlcvRule()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100.0,
            raw_high=90.0, # High < Open
            raw_low=85.0,
            raw_close=95.0,
            raw_volume=1000.0
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "High (90.0) must be >=" in results[0].message
    assert not results[0].is_valid

@pytest.mark.asyncio
async def test_ohlcv_rule_negative_price(base_context):
    rule = OhlcvRule()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=-100.0,
            raw_high=105.0,
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 2
    messages = [r.message for r in results]
    assert any("Prices cannot be negative" in m for m in messages)
