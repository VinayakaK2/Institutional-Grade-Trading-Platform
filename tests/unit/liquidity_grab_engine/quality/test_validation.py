import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.quality.validation.structural import QualityStructuralValidator
from backend.liquidity_grab_engine.quality.validation.consistency import QualityConsistencyValidator
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext

def test_structural_validator():
    validator = QualityStructuralValidator()
    
    assert validator.validate(None) is False
    
    mock_context = MagicMock()
    mock_context.candidate = None
    assert validator.validate(mock_context) is False
    
    mock_context.candidate = True
    mock_context.candle_series = None
    assert validator.validate(mock_context) is False
    
    mock_context.candle_series = True
    mock_context.configuration = None
    assert validator.validate(mock_context) is False
    
    mock_context.configuration = True
    mock_context.metadata = None
    assert validator.validate(mock_context) is False
    
    mock_context.metadata = True
    assert validator.validate(mock_context) is True

def test_consistency_validator():
    validator = QualityConsistencyValidator()
    
    mock_context = MagicMock()
    mock_context.candidate.parent_trend_snapshot_version = 1
    mock_context.parent_trend_snapshot_version = 2
    assert validator.validate(mock_context) is False
    
    mock_context.parent_trend_snapshot_version = 1
    mock_context.candidate.parent_consolidation_snapshot_version = 1
    mock_context.parent_consolidation_snapshot_version = 2
    assert validator.validate(mock_context) is False
    
    mock_context.parent_consolidation_snapshot_version = 1
    mock_context.candidate.configuration_hash = "hash1"
    mock_context.configuration.generate_hash.return_value = "hash2"
    assert validator.validate(mock_context) is False
    
    mock_context.configuration.generate_hash.return_value = "hash1"
    assert validator.validate(mock_context) is True
