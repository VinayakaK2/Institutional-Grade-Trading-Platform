import pytest
import uuid
from datetime import datetime, timezone, timedelta
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.support_resistance_engine.engine.lifecycle import ZoneLifecycleManager
from backend.support_resistance_engine.models.zone import Zone, ZoneType, ZoneStrength, SwingPoint, SwingType

def test_zone_lifecycle_touches_and_invalidation():
    manager = ZoneLifecycleManager()
    
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    
    swing = SwingPoint(
        type=SwingType.LOW,
        price=1.0,
        timestamp=base_time,
        candle_high=10.0,
        candle_low=1.0,
        candle_open=5.0,
        candle_close=2.0
    )
    
    zone = Zone(
        id=str(uuid.uuid4()),
        symbol=sym,
        timeframe=tf,
        dataset_version="CANONICAL",
        zone_type=ZoneType.SUPPORT,
        center=1.5,
        upper_boundary=2.0,
        lower_boundary=1.0,
        created_at=base_time,
        source_swing_point=swing,
        strength=ZoneStrength(),
        is_active=True
    )
    
    # Create candles
    # Candle 1: Doesn't touch (Low = 3.0)
    c1 = Candle(
        symbol=sym, timeframe=tf, timestamp=base_time + timedelta(days=1),
        open=5.0, high=10.0, low=3.0, close=8.0, volume=100.0, is_completed=True
    )
    
    # Candle 2: Touches but doesn't break (Low = 1.5, Close = 3.0)
    c2 = Candle(
        symbol=sym, timeframe=tf, timestamp=base_time + timedelta(days=2),
        open=5.0, high=10.0, low=1.5, close=3.0, volume=100.0, is_completed=True
    )
    
    # Candle 3: Invalidation break (Low = 0.5, Close = 0.8 -> Close < LowerBoundary)
    c3 = Candle(
        symbol=sym, timeframe=tf, timestamp=base_time + timedelta(days=3),
        open=2.0, high=5.0, low=0.5, close=0.8, volume=100.0, is_completed=True
    )
    
    # First update
    zones = manager.update_zones([zone], [c1, c2])
    
    assert len(zones) == 1
    assert zones[0].is_active == True
    assert zones[0].strength.touch_count == 1
    assert zones[0].strength.rejection_count == 1
    assert zones[0].strength.zone_age_candles == 2
    assert zones[0].strength.last_interaction_timestamp == c2.timestamp
    
    # Second update
    zones = manager.update_zones([zone], [c3])
    
    assert zones[0].is_active == False
    assert zones[0].strength.touch_count == 2
    assert zones[0].strength.rejection_count == 1  # Not incremented because it broke
    assert zones[0].strength.zone_age_candles == 3
    
def test_zone_merging():
    manager = ZoneLifecycleManager()
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    
    swing = SwingPoint(
        type=SwingType.LOW,
        price=1.0,
        timestamp=base_time,
        candle_high=10.0,
        candle_low=1.0,
        candle_open=5.0,
        candle_close=2.0
    )
    
    # Overlapping zones
    z1 = Zone(
        id=str(uuid.uuid4()), symbol=sym, timeframe=tf, dataset_version="CANONICAL",
        zone_type=ZoneType.SUPPORT, center=2.5, upper_boundary=3.0, lower_boundary=2.0,
        created_at=base_time, source_swing_point=swing, strength=ZoneStrength(touch_count=1), is_active=True
    )
    
    z2 = Zone(
        id=str(uuid.uuid4()), symbol=sym, timeframe=tf, dataset_version="CANONICAL",
        zone_type=ZoneType.SUPPORT, center=3.5, upper_boundary=4.0, lower_boundary=2.5,
        created_at=base_time, source_swing_point=swing, strength=ZoneStrength(touch_count=2), is_active=True
    )
    
    z3 = Zone(
        id=str(uuid.uuid4()), symbol=sym, timeframe=tf, dataset_version="CANONICAL",
        zone_type=ZoneType.SUPPORT, center=10.5, upper_boundary=11.0, lower_boundary=10.0,
        created_at=base_time, source_swing_point=swing, strength=ZoneStrength(), is_active=True
    )
    
    merged = manager.merge_zones([z1, z2, z3])
    
    assert len(merged) == 2
    
    # One is 2.0 to 4.0
    big_zone = [z for z in merged if z.upper_boundary == 4.0][0]
    assert big_zone.lower_boundary == 2.0
    assert big_zone.center == 3.0
    assert big_zone.strength.touch_count == 3
    
    # The other is 10.0 to 11.0
    small_zone = [z for z in merged if z.upper_boundary == 11.0][0]
    assert small_zone.lower_boundary == 10.0
