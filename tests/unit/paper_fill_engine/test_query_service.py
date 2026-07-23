import pytest
from unittest.mock import MagicMock
from backend.paper_fill_engine.services.query_service import PaperFillQueryService
from backend.paper_fill_engine.models.fill import FillState

def test_query_service_read_only():
    mock_repo = MagicMock()
    service = PaperFillQueryService(repository=mock_repo)
    
    with pytest.raises(NotImplementedError):
        service.query_by_symbol("AAPL")
        
    with pytest.raises(NotImplementedError):
        service.query_by_timeframe("1D")
        
    with pytest.raises(NotImplementedError):
        service.query_by_parent_snapshot("v1")
        
    with pytest.raises(NotImplementedError):
        service.query_by_fill_state(FillState.PENDING_FILL)
