import pytest
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext

@pytest.fixture
def dummy_metadata():
    return {"request_id": "req-fill-123"}

@pytest.fixture
def dummy_configuration():
    return {
        "requested_quantity": 100,
        "simulated_fills": []
    }

@pytest.fixture
def dummy_context(dummy_configuration, dummy_metadata):
    return PaperFillExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )

@pytest.fixture
def dummy_pipeline_context(dummy_context):
    return PaperFillPipelineContext(execution_context=dummy_context)
