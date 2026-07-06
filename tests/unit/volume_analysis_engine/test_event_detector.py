import pytest
from datetime import datetime, timezone, timedelta
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, RVOLClassification, VolumeEventType, CandleClassification
from backend.volume_analysis_engine.engine.event_detector import VolumeEventDetector
import uuid

def create_candle(open_p: float, close_p: float, ts: datetime) -> Candle:
    return Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        timestamp=ts,
        open=open_p,
        high=max(open_p, close_p) + 5,
        low=min(open_p, close_p) - 5,
        close=close_p,
        volume=100.0
    )

def create_result(rvol: float, ts: datetime) -> VolumeAnalysisResult:
    return VolumeAnalysisResult(
        id=str(uuid.uuid4()),
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        dataset_version="v1",
        timestamp=ts,
        volume=100.0,
        avg_volume=100.0 / rvol if rvol > 0 else 100.0,
        rvol=rvol,
        classification=RVOLClassification.NORMAL
    )

def test_event_detector_classifications():
    detector = VolumeEventDetector()
    config = VolumeAnalysisConfig(
        expansion_threshold=1.5,
        contraction_threshold=0.7,
        climax_threshold=3.0,
        dry_volume_threshold=0.3
    )
    
    ts = datetime.now(timezone.utc)
    # Candle 1: Bullish Climax (RVOL=3.0, Close > Open)
    c1 = create_candle(100.0, 110.0, ts)
    r1 = create_result(3.0, ts)
    
    # Candle 2: Bearish Contraction (RVOL=0.7, Close < Open)
    c2 = create_candle(110.0, 100.0, ts + timedelta(days=1))
    r2 = create_result(0.7, ts + timedelta(days=1))
    
    # Candle 3: Neutral Dry (RVOL=0.3, Close == Open)
    c3 = create_candle(100.0, 100.0, ts + timedelta(days=2))
    r3 = create_result(0.3, ts + timedelta(days=2))
    
    events = detector.detect_events([c1, c2, c3], [r1, r2, r3], config, [])
    
    # Candle 1 should produce EXPANSION and CLIMAX
    c1_events = [e for e in events if e.timestamp == c1.timestamp]
    assert len(c1_events) == 2
    assert any(e.event_type == VolumeEventType.CLIMAX for e in c1_events)
    assert any(e.event_type == VolumeEventType.EXPANSION for e in c1_events)
    assert c1_events[0].candle_classification == CandleClassification.BULLISH
    
    # Candle 2 should produce CONTRACTION
    c2_events = [e for e in events if e.timestamp == c2.timestamp]
    assert len(c2_events) == 1
    assert c2_events[0].event_type == VolumeEventType.CONTRACTION
    assert c2_events[0].candle_classification == CandleClassification.BEARISH
    
    # Candle 3 should produce DRY and CONTRACTION
    c3_events = [e for e in events if e.timestamp == c3.timestamp]
    assert len(c3_events) == 2
    assert any(e.event_type == VolumeEventType.DRY_VOLUME for e in c3_events)
    assert any(e.event_type == VolumeEventType.CONTRACTION for e in c3_events)
    assert c3_events[0].candle_classification == CandleClassification.NEUTRAL

def test_consecutive_events():
    detector = VolumeEventDetector()
    config = VolumeAnalysisConfig(expansion_threshold=1.5)
    
    ts = datetime.now(timezone.utc)
    candles = [create_candle(100, 110, ts + timedelta(days=i)) for i in range(4)]
    
    # 3 consecutive expansions, then a break
    results = [
        create_result(1.6, ts),
        create_result(1.5, ts + timedelta(days=1)),
        create_result(2.0, ts + timedelta(days=2)),
        create_result(1.0, ts + timedelta(days=3)) # Break
    ]
    
    events = detector.detect_events(candles, results, config, [])
    
    exp_events = [e for e in events if e.event_type == VolumeEventType.EXPANSION]
    assert len(exp_events) == 3
    assert exp_events[0].metadata["consecutive_count"] == 1
    assert exp_events[1].metadata["consecutive_count"] == 2
    assert exp_events[2].metadata["consecutive_count"] == 3
