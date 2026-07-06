import pytest
from backend.indicator_engine.engine.validation import IndicatorValidationEngine
from backend.indicator_engine.engine.engine import IndicatorEngine
from backend.indicator_engine.calculators.sma import SMACalculator
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from datetime import datetime, timedelta

def get_test_candles(num_candles: int = 5) -> list:
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    candles = []
    base_price = 100.0
    for i in range(num_candles):
        candles.append(Candle(
            symbol=symbol,
            timeframe=tf,
            timestamp=datetime(2023, 1, 1) + timedelta(days=i),
            open=str(base_price),
            high=str(base_price + 1),
            low=str(base_price - 1),
            close=str(base_price),
            volume="1000"
        ))
    return candles

def test_validation_engine_valid():
    candles = get_test_candles(5)
    IndicatorValidationEngine.validate(candles) # Should not raise

def test_validation_engine_empty():
    with pytest.raises(ValueError, match="Empty candle series"):
        IndicatorValidationEngine.validate([])

def test_validation_engine_duplicate():
    candles = get_test_candles(5)
    candles[2].timestamp = candles[1].timestamp
    with pytest.raises(ValueError, match="Duplicate timestamp"):
        IndicatorValidationEngine.validate(candles)

def test_validation_engine_unordered():
    candles = get_test_candles(5)
    candles[2].timestamp, candles[3].timestamp = candles[3].timestamp, candles[2].timestamp
    with pytest.raises(ValueError, match="chronological order"):
        IndicatorValidationEngine.validate(candles)

def test_validation_engine_mixed_symbol():
    candles = get_test_candles(5)
    candles[2].symbol = SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ"))
    with pytest.raises(ValueError, match="mixed symbols"):
        IndicatorValidationEngine.validate(candles)

def test_indicator_engine():
    calc = SMACalculator()
    engine = IndicatorEngine([calc])
    
    candles = get_test_candles(20)
    # We pass period via the fact that SMA defaults to 14
    results = engine.calculate_all(candles, "CANONICAL")
    assert len(results) == 7
    
    # Test incremental with no previous state for SMA (SMA doesn't use previous_state, but we can pass it)
    incremental_results = engine.calculate_all(candles[-14:], "CANONICAL", previous_states={"sma": {}})
    assert len(incremental_results) == 1
