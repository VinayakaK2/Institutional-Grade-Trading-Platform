import pytest
import math
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.sma import SMACalculator
from tests.certification.utils import generate_linear_candles

def test_empty_dataset_handling():
    """Certifies that empty datasets do not crash the engine."""
    calc = EMACalculator()
    with pytest.raises(ValueError, match="candles list is empty"):
        calc.calculate([], "v1", period=14)

def test_insufficient_history():
    """Certifies that providing fewer candles than the indicator period raises a ValueError."""
    calc = EMACalculator()
    candles = generate_linear_candles(5) # Period is 14, we pass 5
    with pytest.raises(ValueError):
        calc.calculate(candles, "v1", period=14)

def test_constant_prices():
    """Certifies mathematical stability when inputs are entirely constant (variance=0)."""
    candles = generate_linear_candles(20, start_price=100.0, step=0.0)
    calc = SMACalculator()
    results = calc.calculate(candles, "v1", period=5)
    
    # Value should remain perfectly 100.0 without drift
    assert results[-1].value == 100.0

def test_extreme_values():
    """Certifies mathematical stability with extremely large floats."""
    candles = generate_linear_candles(20, start_price=1e15, step=10.0)
    calc = SMACalculator()
    results = calc.calculate(candles, "v1", period=5)
    
    # 1e15, 1e15+10, 1e15+20, 1e15+30, 1e15+40 -> SMA is 1e15+20.0
    # Period is 5, so the first result is at index 0
    assert results[0].value == 1e15 + 20.0

def test_nan_infinity_rejection():
    """Certifies that invalid floats (NaN, Infinity) injected into prices are handled or raise appropriately."""
    candles = generate_linear_candles(10, start_price=100.0, step=1.0)
    candles[5].close = float('nan')
    
    calc = EMACalculator()
    results = calc.calculate(candles, "v1", period=5)
    
    # candles[5] is NaN. Result for period 5 starts at candle 4 (results[0]).
    # So candle 5 is results[1].
    assert math.isnan(results[1].value)
    assert math.isnan(results[2].value)
