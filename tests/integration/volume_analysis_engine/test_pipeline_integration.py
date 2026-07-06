import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.database.orm.base import Base
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle

from backend.volume_analysis_engine.engine.rvol import RelativeVolumeAnalyzer, VolumeClassifier
from backend.volume_analysis_engine.engine.event_detector import VolumeEventDetector
from backend.volume_analysis_engine.engine.engine import VolumeAnalysisEngine
from backend.volume_analysis_engine.infrastructure.repository import PostgreSQLVolumeRepository
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig, AverageVolumeType

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def create_candle(ts: datetime, volume: float) -> Candle:
    return Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        timestamp=ts,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=volume
    )

def test_volume_engine_integration(db_session):
    analyzer = RelativeVolumeAnalyzer()
    classifier = VolumeClassifier()
    detector = VolumeEventDetector()
    repo = PostgreSQLVolumeRepository(db_session)
    
    engine = VolumeAnalysisEngine(
        rvol_analyzer=analyzer,
        volume_classifier=classifier,
        event_detector=detector,
        repository=repo
    )
    
    # We set minimum_history to a small number for testing
    config = VolumeAnalysisConfig(
        avg_volume_type=AverageVolumeType.SMA,
        avg_volume_period=2,
        minimum_history_required=2,
        expansion_threshold=1.5,
        contraction_threshold=0.7,
        climax_threshold=3.0,
        dry_volume_threshold=0.3
    )
    
    ts = datetime.now(timezone.utc)
    
    # Candle 1: vol = 100
    # Candle 2: vol = 100 -> SMA(2) = 100. RVOL = 1.0
    # Candle 3: vol = 200 -> SMA(2) = 150. RVOL = 1.333
    # Candle 4: vol = 450 -> SMA(2) = 325. RVOL = 1.38
    # Candle 5: vol = 1000 -> SMA(2) = 725. RVOL = 1.37
    # Let's craft it to trigger events
    
    # c1: vol=100
    # c2: vol=100 (SMA2=100) rvol=1.0
    # c3: vol=200 (SMA2=150) rvol=1.33
    # c4: vol=600 (SMA2=400) rvol=1.5 -> EXPANSION
    # c5: vol=1200 (SMA2=900) rvol=1.33 -> NORMAL
    # c6: vol=3000 (SMA2=2100) rvol=1.42 -> NORMAL
    # c7: vol=9000 (SMA2=6000) rvol=1.5 -> EXPANSION
    # let's just make it simple:
    
    candles = [
        create_candle(ts, 100),
        create_candle(ts + timedelta(days=1), 100), # avg 100, rvol 1
        create_candle(ts + timedelta(days=2), 300), # avg 200, rvol 1.5 -> EXPANSION
        create_candle(ts + timedelta(days=3), 60),  # avg 180, rvol 0.33 -> CONTRACTION
        create_candle(ts + timedelta(days=4), 3000), # avg 1530, rvol 1.96 -> EXPANSION
        create_candle(ts + timedelta(days=5), 6000)  # avg 4500, rvol 1.33 -> NORMAL
    ]
    
    # Overwrite candle 4 to trigger climax
    # If C3 = 60
    # C4 = 3000 -> avg = (60+3000)/2 = 1530. RVOL = 1.96. Not a climax (needs 3.0).
    # To get RVOL = 3.0 on SMA(2):
    # Vol_i / ((Vol_i + Vol_{i-1}) / 2) >= 3.0
    # 2 * Vol_i >= 3 Vol_i + 3 Vol_{i-1} -> -Vol_i >= 3 Vol_{i-1} (impossible for positive volume)
    # Wait, SMA is calculated up to current candle including current candle in the IndicatorEngine.
    # Ah! IndicatorEngine's SMA uses `prices[:period]`. Yes, the current candle is in the window.
    # If the current candle is huge, it pulls up the SMA significantly.
    # For a climax, maybe EMA is better, or a larger SMA period (e.g. 20) where one candle's impact is 1/20th.
    
    # Let's use SMA(5) to test climax
    config_climax = VolumeAnalysisConfig(
        avg_volume_type=AverageVolumeType.SMA,
        avg_volume_period=5,
        minimum_history_required=2,
        climax_threshold=3.0,
        expansion_threshold=1.5
    )
    
    candles_climax = [
        create_candle(ts, 100),
        create_candle(ts + timedelta(days=1), 100),
        create_candle(ts + timedelta(days=2), 100),
        create_candle(ts + timedelta(days=3), 100),
        create_candle(ts + timedelta(days=4), 100), # SMA5 = 100. RVOL = 1.0
        create_candle(ts + timedelta(days=5), 1000) # SMA5 = 1400/5 = 280. RVOL = 1000/280 = 3.57 -> CLIMAX & EXPANSION
    ]
    
    results, events = engine.process_candles(candles_climax, "v1", config_climax)
    
    assert len(results) == 2 # Only candles from index 4 onwards have an SMA(5)
    
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    
    db_results = repo.get_analysis_results(sym, tf, "v1")
    db_events = repo.get_events(sym, tf, "v1")
    
    assert len(db_results) == len(results)
    assert len(db_events) == len(events)
    
    # We expect 2 events on the 6th candle (Climax, Expansion)
    assert len(events) == 2
    event_types = [e.event_type.value for e in events]
    assert "climax" in event_types
    assert "expansion" in event_types
