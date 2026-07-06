import pytest
from datetime import datetime, timezone, timedelta
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig, AverageVolumeType
from backend.volume_analysis_engine.engine.rvol import RelativeVolumeAnalyzer, VolumeClassifier
from backend.volume_analysis_engine.engine.event_detector import VolumeEventDetector
from backend.volume_analysis_engine.engine.engine import VolumeAnalysisEngine
from backend.volume_analysis_engine.contracts.repository import VolumeAnalysisRepositoryContract

class MockRepository(VolumeAnalysisRepositoryContract):
    def __init__(self):
        self.results = []
        self.events = []
    
    def save_analysis(self, results, events):
        self.results.extend(results)
        self.events.extend(events)
        
    def get_analysis_results(self, symbol, timeframe, dataset_version, limit=None):
        return self.results
        
    def get_events(self, symbol, timeframe, dataset_version, limit=None):
        return self.events

def create_candle(ts: datetime, volume: float) -> Candle:
    return Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        timestamp=ts,
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=volume
    )

def test_engine_end_to_end_sma():
    repo = MockRepository()
    engine = VolumeAnalysisEngine(
        RelativeVolumeAnalyzer(),
        VolumeClassifier(),
        VolumeEventDetector(),
        repo
    )
    
    config = VolumeAnalysisConfig(
        avg_volume_type=AverageVolumeType.SMA,
        avg_volume_period=2,
        minimum_history_required=2
    )
    
    ts = datetime.now(timezone.utc)
    # 4 candles. SMA(2) will start emitting at index 1 (candle 2).
    # Candles available with SMA:
    # C2: vol=200, avg=150
    # C3: vol=300, avg=250
    # C4: vol=600, avg=450
    candles = [
        create_candle(ts, 100),
        create_candle(ts + timedelta(days=1), 200),
        create_candle(ts + timedelta(days=2), 300),
        create_candle(ts + timedelta(days=3), 600)
    ]
    
    results, events = engine.process_candles(candles, "v1", config)
    
    # We expect 3 results, since the first candle doesn't have an SMA yet.
    assert len(results) == 3
    assert results[0].volume == 200
    assert results[0].avg_volume == 150.0
    
    assert results[1].volume == 300
    assert results[1].avg_volume == 250.0
    
    assert results[2].volume == 600
    assert results[2].avg_volume == 450.0
    
    assert len(repo.results) == 3
