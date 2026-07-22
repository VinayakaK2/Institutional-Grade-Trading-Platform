import pytest
from backend.paper_execution_engine.services.query_service import PaperExecutionQueryService

from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_query_service_read_only():
    mock_repo = AsyncMock()
    service = PaperExecutionQueryService(repository=mock_repo)
    
    await service.query_latest()
    mock_repo.load_latest.assert_called_once()
    
    await service.query_by_snapshot_version("v_123")
    mock_repo.load_by_snapshot_version.assert_called_once_with("v_123")
    
    with pytest.raises(NotImplementedError):
        await service.query_by_symbol("AAPL")
        
    with pytest.raises(NotImplementedError):
        await service.query_by_timeframe("1D")
        
    with pytest.raises(NotImplementedError):
        await service.query_by_dataset_version("v1")
        
    with pytest.raises(NotImplementedError):
        await service.query_by_parent_portfolio_decision_snapshot("p_v_1")
