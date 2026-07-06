import pytest
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.detectors.anomalies import AnomalyDetector
from backend.data_validation.contracts.rule import ValidationContext

@pytest.fixture
def base_context():
    return ValidationContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        provider="test_provider",
        dependencies={"anomaly_config": {"max_price_change_pct": 50.0, "max_volume_spike_ratio": 100.0}}
    )

@pytest.mark.asyncio
async def test_anomaly_detector_no_anomaly(base_context):
    rule = AnomalyDetector()
    records = [
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100, raw_high=110, raw_low=95, raw_close=105, raw_volume=1000
        ),
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-02T00:00:00Z",
            raw_open=105, raw_high=115, raw_low=100, raw_close=110, raw_volume=1200
        )
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_anomaly_detector_price_spike(base_context):
    rule = AnomalyDetector()
    records = [
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100, raw_high=110, raw_low=95, raw_close=100, raw_volume=1000
        ),
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-02T00:00:00Z",
            raw_open=100, raw_high=200, raw_low=100, raw_close=200, raw_volume=1000
        ) # Price doubled
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "Extreme price change" in results[0].message
    
@pytest.mark.asyncio
async def test_anomaly_detector_volume_spike(base_context):
    rule = AnomalyDetector()
    records = [
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-01T00:00:00Z",
            raw_open=100, raw_high=110, raw_low=95, raw_close=100, raw_volume=1000
        ),
        RawCandle(
            provider="test", symbol=base_context.symbol, timeframe=base_context.timeframe,
            raw_timestamp="2024-01-02T00:00:00Z",
            raw_open=100, raw_high=110, raw_low=95, raw_close=100, raw_volume=150000
        ) # > 100x volume
    ]
    results = await rule.validate(base_context, records)
    assert len(results) == 1
    assert "Extreme volume spike" in results[0].message
