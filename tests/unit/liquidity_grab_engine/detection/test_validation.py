import pytest
import unittest.mock as mock
from backend.liquidity_grab_engine.detection.validation.structural import DetectionStructuralValidator
from backend.liquidity_grab_engine.detection.validation.consistency import DetectionConsistencyValidator

def test_structural_validation():
    context = mock.MagicMock()
    context.dataset = None
    
    with pytest.raises(ValueError, match="dataset context is missing"):
        DetectionStructuralValidator.validate(context)
        
    context.dataset = mock.MagicMock()
    context.parent_snapshots = None
    with pytest.raises(ValueError, match="parent_snapshots context is missing"):
        DetectionStructuralValidator.validate(context)
        
    context.parent_snapshots = mock.MagicMock()
    context.market_data = None
    with pytest.raises(ValueError, match="market_data context is missing"):
        DetectionStructuralValidator.validate(context)
        
    context.market_data = mock.MagicMock()
    context.configuration = None
    with pytest.raises(ValueError, match="configuration is missing"):
        DetectionStructuralValidator.validate(context)
        
    context.configuration = mock.MagicMock()
    context.metadata = None
    with pytest.raises(ValueError, match="metadata is missing"):
        DetectionStructuralValidator.validate(context)
        
    context.metadata = mock.MagicMock()
    context.market_data.symbol = None
    with pytest.raises(ValueError, match="symbol is missing from market_data"):
        DetectionStructuralValidator.validate(context)
        
    context.market_data.symbol = mock.MagicMock()
    context.market_data.timeframe = None
    with pytest.raises(ValueError, match="timeframe is missing from market_data"):
        DetectionStructuralValidator.validate(context)
        
    context.market_data.timeframe = mock.MagicMock()
    context.market_data.candle_series = None
    with pytest.raises(ValueError, match="candle_series is missing from market_data"):
        DetectionStructuralValidator.validate(context)

def test_structural_validation_none_context():
    with pytest.raises(ValueError, match="Detection Context cannot be None"):
        DetectionStructuralValidator.validate(None)

def test_consistency_validation():
    context = mock.MagicMock()
    context.dataset.version = 0
    
    with pytest.raises(ValueError, match="Invalid dataset version"):
        DetectionConsistencyValidator.validate(context)
        
    context.dataset.version = 1
    context.parent_snapshots.trend_snapshot_version = 0
    with pytest.raises(ValueError, match="Invalid parent trend snapshot version"):
        DetectionConsistencyValidator.validate(context)
        
    context.parent_snapshots.trend_snapshot_version = 1
    context.parent_snapshots.consolidation_snapshot_version = -1
    with pytest.raises(ValueError, match="Invalid parent consolidation snapshot version"):
        DetectionConsistencyValidator.validate(context)
