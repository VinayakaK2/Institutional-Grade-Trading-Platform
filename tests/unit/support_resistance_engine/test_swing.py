import pytest
from datetime import datetime, timezone, timedelta
from typing import List

from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.support_resistance_engine.engine.swing import SwingDetector
from backend.support_resistance_engine.models.zone import SwingType

@pytest.fixture
def sample_candles() -> List[Candle]:
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    # Let's create 20 candles
    # Candle 5 is a swing high (highest between 0-10)
    # Candle 15 is a swing low (lowest between 10-19)
    candles = []
    
    for i in range(20):
        # Default flat
        c_high = 10.0
        c_low = 5.0
        
        if i == 5:
            c_high = 20.0
        elif i == 15:
            c_low = 1.0
            
        # Add an equal high at 7, just slightly lower than 5 to not break 5, 
        # wait, let's make an equal high somewhere else to test it.
        # We'll make a separate test for equal highs.
        
        candles.append(Candle(
            symbol=sym,
            timeframe=tf,
            timestamp=base_time + timedelta(days=i),
            open=7.0,
            high=c_high,
            low=c_low,
            close=8.0,
            volume=100.0,
            is_completed=True
        ))
    return candles

def test_swing_detector(sample_candles):
    detector = SwingDetector(lookback=3, lookforward=3)
    swings = detector.detect_swings(sample_candles)
    
    # We should have a swing high at index 5
    # and a swing low at index 15
    # Let's check: 
    # High at 5 is 20.0 (highest in [2, 8])
    # Low at 15 is 1.0 (lowest in [12, 18])
    
    # The default flat candles will also trigger a lot of equal highs/lows.
    # Oh wait! Since the other candles are 10.0 high and 5.0 low, 
    # and the detector ignores subsequent equals, the very FIRST candle in any 7-candle window might be a swing if others are equal.
    # Wait, my logic says compare_high > current_high or compare_high == current_high and j < i.
    # So if there's a flat plateau, the FIRST one is a swing high.
    
    assert len(swings) >= 2
    
    high_5 = [s for s in swings if s.price == 20.0 and s.type == SwingType.HIGH]
    assert len(high_5) == 1
    assert high_5[0].timestamp == sample_candles[5].timestamp
    
    low_15 = [s for s in swings if s.price == 1.0 and s.type == SwingType.LOW]
    assert len(low_15) == 1
    assert low_15[0].timestamp == sample_candles[15].timestamp

def test_equal_highs():
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    
    candles = []
    # 7 candles, lookback 2, lookforward 2
    # indices 0-6
    # 0: high=10
    # 1: high=12
    # 2: high=15 (equal high)
    # 3: high=14
    # 4: high=15 (equal high)
    # 5: high=12
    # 6: high=10
    highs = [10.0, 12.0, 15.0, 14.0, 15.0, 12.0, 10.0]
    
    for i, h in enumerate(highs):
        candles.append(Candle(
            symbol=sym,
            timeframe=tf,
            timestamp=base_time + timedelta(days=i),
            open=7.0,
            high=h,
            low=5.0,
            close=8.0,
            volume=100.0,
            is_completed=True
        ))
        
    detector = SwingDetector(lookback=2, lookforward=2)
    swings = detector.detect_swings(candles)
    
    # For index 2 (val 15): window [0, 4]. Compare to 4 (val 15). 
    # j (4) > i (2) is false. So j is NOT < i. It survives and IS a swing high.
    # For index 4 (val 15): window [2, 6]. Compare to 2 (val 15).
    # j (2) < i (4) is true. It DOES NOT survive, so it's NOT a swing high.
    
    highs = [s for s in swings if s.type == SwingType.HIGH]
    # In index 2 window, it's the highest.
    # What about index 1? window [0, 3]. Has 15 inside, so not a swing high.
    
    assert len(highs) == 1
    assert highs[0].timestamp == candles[2].timestamp
