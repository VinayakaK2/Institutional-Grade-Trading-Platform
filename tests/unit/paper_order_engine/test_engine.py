import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.paper_order_engine.core.engine import PaperOrderEngine
from backend.paper_order_engine.core.pipeline import PipelineExecutor
from backend.paper_order_engine.builders.snapshot_builder import PaperOrderSnapshotBuilder
from backend.paper_order_engine.repository.memory_repo import MemoryPaperOrderRepository
from backend.paper_order_engine.validation.structural import StructuralValidator
from backend.paper_order_engine.validation.consistency import ConsistencyValidator
from backend.paper_order_engine.exceptions.exceptions import PaperOrderValidationError, PaperOrderConsistencyError

@pytest.fixture
def engine():
    repo = MemoryPaperOrderRepository()
    mock_consistency = ConsistencyValidator()
    # Mocking validate to return a passed report
    from backend.paper_order_engine.validation.models import ValidationReport
    mock_report = ValidationReport()
    mock_consistency.validate = AsyncMock(return_value=mock_report)
    
    return PaperOrderEngine(
        repository=repo,
        structural_validator=StructuralValidator(),
        consistency_validator=mock_consistency,
        pipeline_executor=PipelineExecutor(),
        snapshot_builder=PaperOrderSnapshotBuilder()
    )

@pytest.mark.asyncio
async def test_engine_empty_pipeline_success(engine, dummy_context):
    snapshot = await engine.execute(dummy_context)
    
    assert snapshot is not None
    assert engine._repository.load(snapshot.snapshot_id) == snapshot

@pytest.mark.asyncio
async def test_engine_structural_failure(engine, dummy_metadata):
    from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext
    bad_context = PaperOrderExecutionContext(
        symbol="",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration={"order_type": "MARKET"},
        metadata=dummy_metadata
    )
    with pytest.raises(PaperOrderValidationError):
        await engine.execute(bad_context)

@pytest.mark.asyncio
async def test_engine_consistency_failure(engine, dummy_context):
    from backend.paper_order_engine.validation.models import ValidationReport
    mock_report = ValidationReport(passed=False, errors=["Consistency Error"])
    engine._consistency_validator.validate = AsyncMock(return_value=mock_report)
    
    with pytest.raises(PaperOrderConsistencyError):
        await engine.execute(dummy_context)

@pytest.mark.asyncio
async def test_engine_propagates_warnings(engine, dummy_context):
    from backend.paper_order_engine.validation.models import ValidationReport
    
    # Structural warnings
    mock_structural = MagicMock()
    mock_report_structural = ValidationReport(passed=True, warnings=["Struct Warning"])
    mock_structural.validate.return_value = mock_report_structural
    engine._structural_validator = mock_structural
    
    # Consistency warnings
    mock_report_consistency = ValidationReport(passed=True, warnings=["Consist Warning"])
    engine._consistency_validator.validate = AsyncMock(return_value=mock_report_consistency)
    
    # Mock pipeline executor to capture pipeline_context
    mock_executor = AsyncMock()
    engine._pipeline_executor = mock_executor
    
    await engine.execute(dummy_context)
    
    # Assert that warnings were injected into pipeline_context
    args, kwargs = mock_executor.execute.call_args
    pipeline_context = args[1]
    
    assert "Struct Warning" in pipeline_context.diagnostics.structural_validation_warnings
    assert "Consist Warning" in pipeline_context.diagnostics.consistency_validation_warnings
