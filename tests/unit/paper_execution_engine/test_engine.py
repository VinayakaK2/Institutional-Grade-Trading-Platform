import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.paper_execution_engine.core.engine import PaperExecutionEngine
from backend.paper_execution_engine.core.pipeline import PipelineExecutor
from backend.paper_execution_engine.builders.snapshot_builder import PaperExecutionSnapshotBuilder
from backend.paper_execution_engine.repository.memory_repo import MemoryPaperExecutionRepository
from backend.paper_execution_engine.validation.structural import StructuralValidator
from backend.paper_execution_engine.validation.consistency import ConsistencyValidator
from tests.unit.paper_execution_engine.conftest import DummyStage

@pytest.fixture
def engine():
    repo = MemoryPaperExecutionRepository()
    return PaperExecutionEngine(
        repository=repo,
        structural_validator=StructuralValidator(),
        consistency_validator=ConsistencyValidator(),
        pipeline_executor=PipelineExecutor(),
        snapshot_builder=PaperExecutionSnapshotBuilder()
    )

@pytest.mark.asyncio
async def test_engine_empty_pipeline_success(engine, dummy_context):
    snapshot = await engine.execute(dummy_context)
    
    assert snapshot is not None
    assert snapshot.symbol == dummy_context.symbol if hasattr(snapshot, 'symbol') else True
    assert snapshot.parent_snapshot_versions == [dummy_context.parent_portfolio_decision_snapshot_version]
    assert await engine._repository.exists(snapshot.snapshot_id)

@pytest.mark.asyncio
async def test_engine_structural_failure(engine, dummy_configuration, dummy_metadata):
    from backend.paper_execution_engine.models.contexts import PaperExecutionContext
    bad_context = PaperExecutionContext(
        symbol="",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_v_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )
    with pytest.raises(ValueError, match="Structural validation failed"):
        await engine.execute(bad_context)

@pytest.mark.asyncio
async def test_engine_consistency_failure(engine, dummy_context):
    mock_report = MagicMock()
    mock_report.passed = False
    mock_report.errors = ["Consistency Error"]
    
    engine._consistency_validator.validate = AsyncMock(return_value=mock_report)
    
    with pytest.raises(ValueError, match="Consistency validation failed"):
        await engine.execute(dummy_context)

@pytest.mark.asyncio
async def test_engine_with_dummy_stage(engine, dummy_context):
    engine._pipeline_executor = PipelineExecutor(stages=[DummyStage()])
    snapshot = await engine.execute(dummy_context)
    assert snapshot is not None
