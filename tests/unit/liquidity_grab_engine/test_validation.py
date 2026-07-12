import pytest
from backend.liquidity_grab_engine.validation.structural import StructuralValidator
from backend.liquidity_grab_engine.validation.consistency import ConsistencyValidator
from backend.liquidity_grab_engine.models.models import LiquidityGrabExecutionContext

import unittest.mock as mock

def test_structural_validation():
    context = mock.MagicMock(spec=LiquidityGrabExecutionContext)
    context.symbol = None
    
    with pytest.raises(ValueError, match="Symbol is missing"):
        StructuralValidator.validate_context(context)
        
    context.symbol = "AAPL"
    context.timeframe = None
    with pytest.raises(ValueError, match="Timeframe is missing"):
        StructuralValidator.validate_context(context)
    
    
    context.timeframe = "1h"
    context.dataset_version = None
    with pytest.raises(ValueError, match="dataset_version is missing"):
        StructuralValidator.validate_context(context)
        
    context.dataset_version = 1
    context.parent_trend_snapshot_version = None
    with pytest.raises(ValueError, match="parent_trend_snapshot_version is missing"):
        StructuralValidator.validate_context(context)
        
    context.parent_trend_snapshot_version = 1
    context.parent_consolidation_snapshot_version = None
    with pytest.raises(ValueError, match="parent_consolidation_snapshot_version is missing"):
        StructuralValidator.validate_context(context)
        
    context.parent_consolidation_snapshot_version = 1
    context.configuration = None
    with pytest.raises(ValueError, match="Configuration is missing"):
        StructuralValidator.validate_context(context)
        
    context.configuration = mock.MagicMock()
    context.metadata = None
    with pytest.raises(ValueError, match="Metadata is missing"):
        StructuralValidator.validate_context(context)

def test_consistency_validation():
    context = mock.MagicMock(spec=LiquidityGrabExecutionContext)
    context.dataset_version = -1
    
    with pytest.raises(ValueError, match="Invalid dataset_version"):
        ConsistencyValidator.validate_lineage(context)
        
    context.dataset_version = 1
    context.parent_trend_snapshot_version = 0
    with pytest.raises(ValueError, match="Invalid parent_trend_snapshot_version"):
        ConsistencyValidator.validate_lineage(context)
        
    context.parent_trend_snapshot_version = 1
    context.parent_consolidation_snapshot_version = 0
    with pytest.raises(ValueError, match="Invalid parent_consolidation_snapshot_version"):
        ConsistencyValidator.validate_lineage(context)
