import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.liquidity_grab_engine.lifecycle.engine.engine import LiquidityGrabLifecycleEngine

@pytest.mark.asyncio
async def test_engine_execution():
    mock_pipeline = MagicMock()
    mock_repo = AsyncMock()
    mock_structural = MagicMock()
    mock_consistency = MagicMock()
    
    mock_snapshot = MagicMock()
    mock_snapshot.snapshot_id = "snap1"
    mock_pipeline.execute.return_value = mock_snapshot
    
    engine = LiquidityGrabLifecycleEngine(mock_pipeline, mock_repo, mock_structural, mock_consistency)
    
    mock_context = MagicMock()
    mock_context.candidate.candidate_id = "c1"
    
    result = await engine.execute(mock_context)
    
    assert result == mock_snapshot
    mock_structural.validate.assert_called_once_with(mock_context)
    mock_consistency.validate.assert_called_once_with(mock_context)
    mock_pipeline.execute.assert_called_once_with(mock_context)
    mock_repo.save.assert_called_once_with(mock_snapshot)
