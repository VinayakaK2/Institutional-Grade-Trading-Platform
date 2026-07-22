import pytest
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext
from backend.paper_order_engine.models.order import OrderType

@pytest.fixture
def dummy_metadata():
    return {"request_id": "req-123"}

@pytest.fixture
def dummy_configuration():
    return {
        "order_type": OrderType.MARKET.value
    }

@pytest.fixture
def dummy_context(dummy_configuration, dummy_metadata):
    return PaperOrderExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )

@pytest.fixture
def dummy_pipeline_context(dummy_context):
    return PaperOrderPipelineContext(execution_context=dummy_context)
