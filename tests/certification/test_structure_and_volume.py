import pytest
from backend.market_structure_engine.engine.analyzer import StructureAnalyzer
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.volume_analysis_engine.engine.rvol import RelativeVolumeAnalyzer, VolumeClassifier
from backend.volume_analysis_engine.models.volume import RVOLClassification
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from datetime import datetime, timezone, timedelta
from tests.certification.utils import generate_v_shape_candles, assert_floats_close

def test_market_structure_sequence_certification():
    """Certifies the generation of HH/HL/LH/LL from a known swing sequence."""
    sym = SymbolReference(symbol="TEST/USD", exchange=ExchangeReference(name="TEST", code="TEST"))
    tf = Timeframe.H1
    base_t = datetime(2025, 1, 1, tzinfo=timezone.utc)
    
    # Simulate an uptrend sequence: Low(100), High(110), Low(105), High(120)
    swings = [
        SwingPoint(timestamp=base_t, price=100.0, type=SwingType.LOW, candle_high=101.0, candle_low=99.0, candle_open=100.0, candle_close=100.0),
        SwingPoint(timestamp=base_t+timedelta(hours=1), price=110.0, type=SwingType.HIGH, candle_high=111.0, candle_low=109.0, candle_open=110.0, candle_close=110.0),
        SwingPoint(timestamp=base_t+timedelta(hours=2), price=105.0, type=SwingType.LOW, candle_high=106.0, candle_low=104.0, candle_open=105.0, candle_close=105.0),
        SwingPoint(timestamp=base_t+timedelta(hours=3), price=120.0, type=SwingType.HIGH, candle_high=121.0, candle_low=119.0, candle_open=120.0, candle_close=120.0)
    ]
    
    analyzer = StructureAnalyzer()
    structure_points = analyzer.classify_swings(swings, previous_structure=[])
    
    assert len(structure_points) == 4
    assert structure_points[0].type == StructureType.HL # Initial Low (Analyzer defaults initial to HL)
    assert structure_points[1].type == StructureType.HH # Initial High
    assert structure_points[2].type == StructureType.HL # Higher Low
    assert structure_points[3].type == StructureType.HH # Higher High
    
def test_relative_volume_certification():
    """Certifies the calculation of RVOL and categorization of Volume Expansion/Climax."""
    # V-Shape candles but we'll override volumes to be deterministic
    candles = generate_v_shape_candles(20)
    
    # Set base volume to 1000
    for c in candles:
        c.volume = 1000.0
        
    # At index 10, inject a climax volume
    candles[10].volume = 4000.0
    
    analyzer = RelativeVolumeAnalyzer()
    classifier = VolumeClassifier()
    config = VolumeAnalysisConfig(lookback_period=10)
    
    # Dummy average volume of 1000.0 for all candles
    avg_volumes = [1000.0] * 20
    
    # Calculate RVOL
    results = analyzer.analyze(candles, avg_volumes, "v1", config)
    
    # Classify RVOL
    results = classifier.classify(results, config)
    
    assert len(results) == 20
    
    # At index 10, the lookback (0 to 9) has volumes of 1000. SMA of volume = 1000.
    # So Average Volume at 10 should be 1000.
    # RVOL = 4000 / 1000 = 4.0
    rvol_10 = results[10]
    assert_floats_close(4.0, rvol_10.rvol, msg="RVOL Climax calculation")
    
    # Ensure classification is HIGH
    assert rvol_10.classification == RVOLClassification.HIGH
