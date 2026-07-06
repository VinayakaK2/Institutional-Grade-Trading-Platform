import pytest
import uuid
from datetime import datetime, timezone
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.market_structure_engine.models.events import EventType, EventSignal
from backend.market_structure_engine.models.config import StructureConfig, ConfirmationRule
from backend.market_structure_engine.engine.event_detector import EventDetector

sym = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
tf = Timeframe.D1

def create_candle(dt: datetime, high: float, low: float, close: float) -> Candle:
    return Candle(
        symbol=sym,
        timeframe=tf,
        timestamp=dt,
        open=low,
        high=high,
        low=low,
        close=close,
        volume=100.0,
        is_completed=True
    )

def create_struct(price: float, s_type: StructureType, dt: datetime) -> MarketStructurePoint:
    swing = SwingPoint(
        type=SwingType.HIGH if s_type in (StructureType.HH, StructureType.LH) else SwingType.LOW,
        price=price,
        timestamp=dt,
        candle_high=price if s_type in (StructureType.HH, StructureType.LH) else price + 1,
        candle_low=price - 1 if s_type in (StructureType.HH, StructureType.LH) else price,
        candle_open=price,
        candle_close=price
    )
    return MarketStructurePoint(id=str(uuid.uuid4()), swing_point=swing, type=s_type)

def test_bullish_bos_wick():
    detector = EventDetector()
    config = StructureConfig(confirmation_rule=ConfirmationRule.WICK_BREAK)
    
    # Structure: HH at 20.0, then HL at 15.0
    pts = [
        create_struct(20.0, StructureType.HH, datetime(2023, 1, 1, tzinfo=timezone.utc)),
        create_struct(15.0, StructureType.HL, datetime(2023, 1, 2, tzinfo=timezone.utc))
    ]
    
    # Candle with wick high = 21.0, close = 19.0, low = 16.0
    candles = [create_candle(datetime(2023, 1, 3, tzinfo=timezone.utc), 21.0, 16.0, 19.0)]
    
    events = detector.detect_events(pts, candles, config, [])
    
    assert len(events) == 1
    assert events[0].type == EventType.BOS
    assert events[0].signal == EventSignal.BULLISH
    assert events[0].reference_swing.price == 20.0

def test_bullish_bos_body():
    detector = EventDetector()
    config = StructureConfig(confirmation_rule=ConfirmationRule.BODY_CLOSE)
    
    pts = [create_struct(20.0, StructureType.HH, datetime(2023, 1, 1, tzinfo=timezone.utc))]
    
    # Wick breaks 20.0, but close is 19.0 (No BOS)
    candles = [create_candle(datetime(2023, 1, 2, tzinfo=timezone.utc), 21.0, 14.0, 19.0)]
    events = detector.detect_events(pts, candles, config, [])
    assert len(events) == 0
    
    # Close breaks 20.0 (BOS)
    candles2 = [create_candle(datetime(2023, 1, 3, tzinfo=timezone.utc), 22.0, 14.0, 21.0)]
    events2 = detector.detect_events(pts, candles2, config, [])
    assert len(events2) == 1
    assert events2[0].type == EventType.BOS

def test_bullish_choch():
    detector = EventDetector()
    config = StructureConfig(confirmation_rule=ConfirmationRule.WICK_BREAK)
    
    # Bearish structure: LH at 20.0, LL at 10.0
    pts = [
        create_struct(20.0, StructureType.LH, datetime(2023, 1, 1, tzinfo=timezone.utc)),
        create_struct(10.0, StructureType.LL, datetime(2023, 1, 2, tzinfo=timezone.utc))
    ]
    
    # Break above LH -> Bullish ChoCH
    candles = [create_candle(datetime(2023, 1, 3, tzinfo=timezone.utc), 21.0, 12.0, 19.0)]
    
    events = detector.detect_events(pts, candles, config, [])
    assert len(events) == 1
    assert events[0].type == EventType.CHOCH
    assert events[0].signal == EventSignal.BULLISH

def test_bearish_bos():
    detector = EventDetector()
    config = StructureConfig(confirmation_rule=ConfirmationRule.WICK_BREAK)
    
    # Bearish structure: LH at 20.0, LL at 10.0
    pts = [
        create_struct(20.0, StructureType.LH, datetime(2023, 1, 1, tzinfo=timezone.utc)),
        create_struct(10.0, StructureType.LL, datetime(2023, 1, 2, tzinfo=timezone.utc))
    ]
    
    # Break below LL -> Bearish BoS
    candles = [create_candle(datetime(2023, 1, 3, tzinfo=timezone.utc), 12.0, 9.0, 11.0)]
    
    events = detector.detect_events(pts, candles, config, [])
    assert len(events) == 1
    assert events[0].type == EventType.BOS
    assert events[0].signal == EventSignal.BEARISH
    
def test_duplicate_events_prevented():
    detector = EventDetector()
    config = StructureConfig(confirmation_rule=ConfirmationRule.WICK_BREAK)
    
    pts = [create_struct(20.0, StructureType.HH, datetime(2023, 1, 1, tzinfo=timezone.utc))]
    
    # Two candles break the same high
    candles = [
        create_candle(datetime(2023, 1, 2, tzinfo=timezone.utc), 21.0, 14.0, 19.0),
        create_candle(datetime(2023, 1, 3, tzinfo=timezone.utc), 22.0, 14.0, 19.0)
    ]
    
    events = detector.detect_events(pts, candles, config, [])
    
    # Should only generate one event for the first break
    assert len(events) == 1
