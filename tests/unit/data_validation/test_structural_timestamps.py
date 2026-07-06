import pytest
from datetime import datetime
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.validation.rules.structural import StructuralRule
from backend.data_validation.contracts.rule import ValidationContext

@pytest.fixture
def base_context():
    return ValidationContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        provider="test_provider"
    )

@pytest.mark.asyncio
async def test_structural_rule_valid_timestamps(base_context):
    rule = StructuralRule()
    
    # integer timestamp
    records = [
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp=1704067200, raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=1),
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp=datetime(2024, 1, 1), raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=1)
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_structural_rule_invalid_timestamp(base_context):
    rule = StructuralRule()
    
    records = [
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp="INVALID_DATE_FORMAT_123", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=1),
        RawCandle(provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe, raw_timestamp=[], raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=1)
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 2
    assert "Invalid timestamp format" in results[0].message
    assert "Invalid timestamp format" in results[1].message
