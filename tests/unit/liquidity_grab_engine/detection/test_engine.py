import pytest
import unittest.mock as mock
from backend.liquidity_grab_engine.detection.engine.engine import LiquidityGrabDetectionEngine
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate
from backend.liquidity_grab_engine.detection.models.context import LiquidityGrabDetectionContext

@pytest.mark.asyncio
async def test_engine_execution_success():
    pipeline = mock.MagicMock()
    candidate = mock.MagicMock(spec=LiquidityGrabCandidate)
    candidate.candidate_id = "123"
    pipeline.execute.return_value = candidate
    
    repository = mock.AsyncMock()
    
    engine = LiquidityGrabDetectionEngine(pipeline, repository)
    
    context = mock.MagicMock()
    
    with mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionStructuralValidator.validate"), \
         mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionConsistencyValidator.validate"):
        result = await engine.execute(context)
        
    assert result == candidate
    repository.save.assert_called_once_with(candidate)

@pytest.mark.asyncio
async def test_engine_execution_no_candidate():
    pipeline = mock.MagicMock()
    pipeline.execute.return_value = None
    
    repository = mock.AsyncMock()
    
    engine = LiquidityGrabDetectionEngine(pipeline, repository)
    
    context = mock.MagicMock()
    
    with mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionStructuralValidator.validate"), \
         mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionConsistencyValidator.validate"):
        result = await engine.execute(context)
        
    assert result is None
    repository.save.assert_not_called()

@pytest.mark.asyncio
async def test_engine_execution_failure():
    pipeline = mock.MagicMock()
    pipeline.execute.side_effect = Exception("Pipeline failed")
    
    repository = mock.AsyncMock()
    
    engine = LiquidityGrabDetectionEngine(pipeline, repository)
    
    context = mock.MagicMock()
    
    with mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionStructuralValidator.validate"), \
         mock.patch("backend.liquidity_grab_engine.detection.engine.engine.DetectionConsistencyValidator.validate"):
        with pytest.raises(Exception, match="Pipeline failed"):
            await engine.execute(context)
