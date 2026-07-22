import pytest
from unittest.mock import MagicMock
from backend.paper_order_engine.services.query_service import PaperOrderQueryService
from backend.paper_order_engine.models.order import OrderState

def test_query_service_read_only():
    mock_repo = MagicMock()
    service = PaperOrderQueryService(repository=mock_repo)
    
    with pytest.raises(NotImplementedError):
        service.query_by_symbol("AAPL")
        
    with pytest.raises(NotImplementedError):
        service.query_by_timeframe("1D")
        
    with pytest.raises(NotImplementedError):
        service.query_by_parent_execution_snapshot("v1")
        
    with pytest.raises(NotImplementedError):
        service.query_by_order_state(OrderState.CREATED)
