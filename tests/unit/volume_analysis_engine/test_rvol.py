import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig
from backend.volume_analysis_engine.engine.rvol import RelativeVolumeAnalyzer, VolumeClassifier
from backend.volume_analysis_engine.models.volume import RVOLClassification

def create_candle(volume: float) -> Candle:
    return Candle(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.D1,
        timestamp=datetime.now(timezone.utc),
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=volume
    )

def test_rvol_calculation():
    analyzer = RelativeVolumeAnalyzer()
    config = VolumeAnalysisConfig(minimum_history_required=2)
    candles = [create_candle(100), create_candle(200)]
    avg_vols = [100.0, 100.0]
    
    results = analyzer.analyze(candles, avg_vols, "v1", config)
    assert len(results) == 2
    assert results[0].rvol == 1.0
    assert results[1].rvol == 2.0
    assert results[0].classification == RVOLClassification.NORMAL
    assert results[1].classification == RVOLClassification.NORMAL

def test_rvol_zero_avg_vol():
    analyzer = RelativeVolumeAnalyzer()
    config = VolumeAnalysisConfig(minimum_history_required=1)
    candles = [create_candle(100)]
    avg_vols = [0.0]
    
    results = analyzer.analyze(candles, avg_vols, "v1", config)
    assert results[0].rvol == 0.0

def test_rvol_insufficient_history():
    analyzer = RelativeVolumeAnalyzer()
    config = VolumeAnalysisConfig(minimum_history_required=5)
    candles = [create_candle(100)]
    avg_vols = [100.0]
    
    with pytest.raises(ValueError, match="Insufficient history"):
        analyzer.analyze(candles, avg_vols, "v1", config)

def test_rvol_mismatch():
    analyzer = RelativeVolumeAnalyzer()
    config = VolumeAnalysisConfig(minimum_history_required=1)
    
    with pytest.raises(ValueError, match="length mismatch"):
        analyzer.analyze([create_candle(100)], [100.0, 200.0], "v1", config)

def test_volume_classifier_boundaries():
    analyzer = RelativeVolumeAnalyzer()
    classifier = VolumeClassifier()
    config = VolumeAnalysisConfig(
        minimum_history_required=1,
        expansion_threshold=1.5,
        contraction_threshold=0.7
    )
    
    # Boundary tests (>= and <= rules)
    candles = [
        create_candle(150), # RVOL = 1.5
        create_candle(149.9999999), # RVOL = 1.499999999
        create_candle(70), # RVOL = 0.7
        create_candle(70.0000001), # RVOL = 0.700000001
        create_candle(100) # RVOL = 1.0
    ]
    avg_vols = [100.0, 100.0, 100.0, 100.0, 100.0]
    
    results = analyzer.analyze(candles, avg_vols, "v1", config)
    classified = classifier.classify(results, config)
    
    assert classified[0].classification == RVOLClassification.HIGH
    assert classified[1].classification == RVOLClassification.NORMAL
    assert classified[2].classification == RVOLClassification.LOW
    assert classified[3].classification == RVOLClassification.NORMAL
    assert classified[4].classification == RVOLClassification.NORMAL
