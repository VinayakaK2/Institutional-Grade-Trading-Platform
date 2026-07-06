import pytest
from datetime import datetime, timezone
from backend.support_resistance_engine.engine.zone_generator import ZoneGenerator
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType, ZoneType

def test_zone_generator():
    generator = ZoneGenerator()
    
    # Swing High
    swing_high = SwingPoint(
        type=SwingType.HIGH,
        price=20.0,
        timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
        candle_high=20.0,
        candle_low=10.0,
        candle_open=15.0,
        candle_close=18.0
    )
    
    # Swing Low
    swing_low = SwingPoint(
        type=SwingType.LOW,
        price=1.0,
        timestamp=datetime(2023, 1, 2, tzinfo=timezone.utc),
        candle_high=10.0,
        candle_low=1.0,
        candle_open=5.0,
        candle_close=2.0
    )
    
    from backend.market_data.models.symbol import SymbolReference, ExchangeReference
    from backend.market_data.models.timeframe import Timeframe
    sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.D1
    zones = generator.generate_zones([swing_high, swing_low], sym, tf, "CANONICAL")
    
    assert len(zones) == 2
    
    # First is resistance
    res = zones[0]
    assert res.zone_type == ZoneType.RESISTANCE
    # Resistance bounds: Upper = High (20), Lower = max(Open, Close) = max(15, 18) = 18
    assert res.upper_boundary == 20.0
    assert res.lower_boundary == 18.0
    assert res.center == 19.0
    
    # Second is support
    sup = zones[1]
    assert sup.zone_type == ZoneType.SUPPORT
    # Support bounds: Lower = Low (1), Upper = min(Open, Close) = min(5, 2) = 2
    assert sup.lower_boundary == 1.0
    assert sup.upper_boundary == 2.0
    assert sup.center == 1.5
