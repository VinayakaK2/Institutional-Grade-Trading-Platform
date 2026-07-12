import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.lifecycle.validation.structural import LifecycleStructuralValidator
from backend.liquidity_grab_engine.lifecycle.validation.consistency import LifecycleConsistencyValidator

def test_structural_validation():
    validator = LifecycleStructuralValidator()
    
    context = MagicMock()
    context.candidate = None
    with pytest.raises(ValueError, match="LiquidityGrabCandidate must not be None"):
        validator.validate(context)
        
    context.candidate = MagicMock()
    context.quality_report = None
    with pytest.raises(ValueError, match="LiquidityGrabQualityReport must not be None"):
        validator.validate(context)
        
    context.quality_report = MagicMock()
    context.evaluation_candles = None
    with pytest.raises(ValueError, match="Evaluation candles must not be None"):
        validator.validate(context)
        
    context.evaluation_candles = MagicMock()
    context.configuration = None
    with pytest.raises(ValueError, match="Configuration must not be None"):
        validator.validate(context)
        
    context.configuration = MagicMock()
    context.dataset_version = -1
    with pytest.raises(ValueError, match="Dataset version must be a positive integer"):
        validator.validate(context)
        
    context.dataset_version = 1
    validator.validate(context)

def test_consistency_validation():
    validator = LifecycleConsistencyValidator()
    context = MagicMock()
    context.candidate.candidate_id = "c1"
    context.quality_report.candidate_id = "c2"
    with pytest.raises(ValueError, match="Candidate ID mismatch"):
        validator.validate(context)
        
    context.quality_report.candidate_id = "c1"
    context.dataset_version = 1
    context.candidate.dataset_version = 2
    with pytest.raises(ValueError, match="Dataset version mismatch"):
        validator.validate(context)
        
    context.candidate.dataset_version = 1
    context.quality_report.dataset_version = 2
    with pytest.raises(ValueError, match="Dataset version mismatch"):
        validator.validate(context)
        
    context.quality_report.dataset_version = 1
    context.configuration.generate_hash.return_value = "hash1"
    context.quality_report.configuration_hash = "hash2"
    with pytest.raises(ValueError, match="Configuration hash mismatch"):
        validator.validate(context)
        
    context.quality_report.configuration_hash = "hash1"
    validator.validate(context)
