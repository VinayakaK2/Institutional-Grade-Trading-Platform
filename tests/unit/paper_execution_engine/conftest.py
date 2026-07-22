import pytest
from backend.paper_execution_engine.models.contexts import (
    PaperExecutionContext,
    PaperExecutionConfiguration,
    PaperExecutionMetadata,
    PaperExecutionPipelineContext
)
from backend.paper_execution_engine.contracts.pipeline import IPaperExecutionPipelineStage

@pytest.fixture
def dummy_configuration():
    return PaperExecutionConfiguration(
        engine_version="1.0.0",
        snapshot_version="1.0.0",
        pipeline_version="1.0.0",
        execution_mode="PAPER",
        validation_level="STRICT"
    )

@pytest.fixture
def dummy_metadata():
    return PaperExecutionMetadata(
        request_id="req-123",
        correlation_id="corr-456",
        created_by="system",
        environment="test",
        notes="Testing"
    )

@pytest.fixture
def dummy_context(dummy_configuration, dummy_metadata):
    return PaperExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_v_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )

@pytest.fixture
def dummy_pipeline_context():
    return PaperExecutionPipelineContext()

class DummyStage(IPaperExecutionPipelineStage):
    async def execute(self, execution_context, pipeline_context):
        pipeline_context.stage_outputs["DummyStage"] = "Executed"
