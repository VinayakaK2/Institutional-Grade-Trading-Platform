import math
from typing import List
from datetime import datetime, timezone, timedelta
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle

def generate_linear_candles(count: int, start_price: float = 100.0, step: float = 1.0) -> List[Candle]:
    """Generates a linear price sequence for deterministic math checks."""
    symbol = SymbolReference(symbol="TEST/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    candles = []
    
    for i in range(count):
        price = start_price + (i * step)
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H1,
            timestamp=base_time + timedelta(hours=i),
            open=price,
            high=price + abs(step),
            low=price - abs(step),
            close=price,
            volume=1000.0 + (i * 10)
        ))
    return candles

def generate_v_shape_candles(count: int, start_price: float = 100.0, swing_depth: float = 10.0) -> List[Candle]:
    """Generates a V-shape market structure dataset to guarantee a distinct Swing Low/High."""
    symbol = SymbolReference(symbol="TEST/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    candles = []
    midpoint = count // 2
    
    for i in range(count):
        if i <= midpoint:
            price = start_price - (i * (swing_depth / midpoint))
        else:
            price = (start_price - swing_depth) + ((i - midpoint) * (swing_depth / midpoint))
            
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H1,
            timestamp=base_time + timedelta(hours=i),
            open=price,
            high=price + 1.0,
            low=price - 1.0,
            close=price,
            volume=1000.0
        ))
    return candles

def generate_alternating_candles(count: int, start_price: float = 100.0) -> List[Candle]:
    """Generates up-down alternating candles."""
    symbol = SymbolReference(symbol="TEST/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    candles = []
    
    for i in range(count):
        direction = 1 if i % 2 == 0 else -1
        price = start_price + (direction * 5.0)
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H1,
            timestamp=base_time + timedelta(hours=i),
            open=start_price,
            high=start_price + 10.0,
            low=start_price - 10.0,
            close=price,
            volume=1000.0
        ))
    return candles

def assert_floats_close(expected: float, actual: float, rel_tol: float = 1e-05, abs_tol: float = 1e-08, msg: str = ""):
    """Helper to enforce strict floating point tolerance checks for certification."""
    if math.isnan(expected) and math.isnan(actual):
        return
    if expected is None and actual is None:
        return
        
    assert math.isclose(expected, actual, rel_tol=rel_tol, abs_tol=abs_tol), \
        f"{msg} | Expected: {expected}, Actual: {actual}, Diff: {abs(expected - actual)}"
