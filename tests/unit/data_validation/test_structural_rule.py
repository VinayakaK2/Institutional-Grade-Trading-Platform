import pytest
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
async def test_structural_rule_valid(base_context):
    rule = StructuralRule()
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
    assert len(results) == 0 # No errors

@pytest.mark.asyncio
async def test_structural_rule_nulls(base_context):
    rule = StructuralRule()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100.0,
            raw_high=None, # Null field
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "raw_high" in results[0].message
    assert not results[0].is_valid

@pytest.mark.asyncio
async def test_structural_rule_invalid_types(base_context):
    rule = StructuralRule()
    records = [
        RawCandle(
            provider="test",
            symbol=base_context.symbol,
            timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open="invalid_string",
            raw_high=105.0,
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "raw_open must be numeric" in results[0].message
    assert not results[0].is_valid
