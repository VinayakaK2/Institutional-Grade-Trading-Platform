import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from backend.liquidity_grab_engine.quality.engine.engine import LiquidityGrabQualityEngine
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport

@pytest.mark.asyncio
async def test_engine_successful_evaluation():
    mock_pipeline = MagicMock()
    mock_report = MagicMock()
    mock_report.report_id = "r1"
    mock_pipeline.execute.return_value = mock_report
    
    mock_repository = AsyncMock()
    
    engine = LiquidityGrabQualityEngine(mock_pipeline, mock_repository)
    
    # Mock validators to return True
    engine.structural_validator = MagicMock()
    engine.structural_validator.validate.return_value = True
    engine.consistency_validator = MagicMock()
    engine.consistency_validator.validate.return_value = True
    
    mock_context = MagicMock()
    
    report = await engine.evaluate(mock_context)
    
    assert report == mock_report
    mock_repository.save.assert_called_once_with(mock_report)

@pytest.mark.asyncio
async def test_engine_validation_failure():
    mock_pipeline = MagicMock()
    mock_repository = AsyncMock()
    
    engine = LiquidityGrabQualityEngine(mock_pipeline, mock_repository)
    
    engine.structural_validator = MagicMock()
    engine.structural_validator.validate.return_value = False
    
    mock_context = MagicMock()
    
    with pytest.raises(ValueError, match="Structural validation failed."):
        await engine.evaluate(mock_context)
        
    mock_repository.save.assert_not_called()
