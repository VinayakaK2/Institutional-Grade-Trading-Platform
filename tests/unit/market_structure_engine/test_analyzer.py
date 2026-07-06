import pytest
from datetime import datetime, timezone
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType
from backend.market_structure_engine.models.structure import StructureType
from backend.market_structure_engine.engine.analyzer import StructureAnalyzer

def create_swing(price: float, type: SwingType, dt: datetime) -> SwingPoint:
    return SwingPoint(
        type=type,
        price=price,
        timestamp=dt,
        candle_high=price if type == SwingType.HIGH else price + 1,
        candle_low=price - 1 if type == SwingType.HIGH else price,
        candle_open=price,
        candle_close=price
    )

def test_structure_classification_basic():
    analyzer = StructureAnalyzer()
    
    swings = [
        create_swing(10.0, SwingType.LOW, datetime(2023, 1, 1, tzinfo=timezone.utc)),
        create_swing(20.0, SwingType.HIGH, datetime(2023, 1, 2, tzinfo=timezone.utc)),
        create_swing(15.0, SwingType.LOW, datetime(2023, 1, 3, tzinfo=timezone.utc)),
        create_swing(25.0, SwingType.HIGH, datetime(2023, 1, 4, tzinfo=timezone.utc)),
        create_swing(12.0, SwingType.LOW, datetime(2023, 1, 5, tzinfo=timezone.utc)),
        create_swing(22.0, SwingType.HIGH, datetime(2023, 1, 6, tzinfo=timezone.utc)),
    ]
    
    points = analyzer.classify_swings(swings, [])
    
    assert len(points) == 6
    assert points[0].type == StructureType.HL # Arbitrary initial low
    assert points[1].type == StructureType.HH # Arbitrary initial high
    assert points[2].type == StructureType.HL # 15 > 10
    assert points[3].type == StructureType.HH # 25 > 20
    assert points[4].type == StructureType.LL # 12 < 15
    assert points[5].type == StructureType.LH # 22 < 25

def test_enforce_alternation():
    analyzer = StructureAnalyzer()
    
    # Sequence with two consecutive highs
    swings = [
        create_swing(10.0, SwingType.LOW, datetime(2023, 1, 1, tzinfo=timezone.utc)),
        create_swing(20.0, SwingType.HIGH, datetime(2023, 1, 2, tzinfo=timezone.utc)),
        create_swing(22.0, SwingType.HIGH, datetime(2023, 1, 3, tzinfo=timezone.utc)),
        create_swing(15.0, SwingType.LOW, datetime(2023, 1, 4, tzinfo=timezone.utc)),
    ]
    
    points = analyzer.classify_swings(swings, [])
    
    # It should keep the HIGHEST high of the consecutive ones (22.0)
    assert len(points) == 3
    assert points[0].swing_point.price == 10.0
    assert points[1].swing_point.price == 22.0
    assert points[1].type == StructureType.HH
    assert points[2].swing_point.price == 15.0

def test_duplicate_timestamps_rejected():
    analyzer = StructureAnalyzer()
    
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    swings = [
        create_swing(10.0, SwingType.LOW, dt),
        create_swing(20.0, SwingType.HIGH, dt),
    ]
    
    with pytest.raises(ValueError, match="Duplicate swing timestamp"):
        analyzer.classify_swings(swings, [])

def test_ignore_older_swings():
    analyzer = StructureAnalyzer()
    
    dt1 = datetime(2023, 1, 1, tzinfo=timezone.utc)
    dt2 = datetime(2023, 1, 2, tzinfo=timezone.utc)
    
    swings1 = [create_swing(10.0, SwingType.LOW, dt1)]
    points1 = analyzer.classify_swings(swings1, [])
    
    # Pass dt1 again, should be ignored
    swings2 = [
        create_swing(10.0, SwingType.LOW, dt1),
        create_swing(20.0, SwingType.HIGH, dt2),
    ]
    points2 = analyzer.classify_swings(swings2, points1)
    
    assert len(points2) == 1
    assert points2[0].swing_point.timestamp == dt2
