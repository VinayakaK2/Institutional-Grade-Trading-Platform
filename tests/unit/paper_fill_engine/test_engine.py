import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.paper_fill_engine.core.engine import PaperFillEngine
from backend.paper_fill_engine.builders.snapshot_builder import PaperFillSnapshotBuilder
from backend.paper_fill_engine.repository.memory_repo import MemoryPaperFillRepository
from backend.paper_fill_engine.validation.structural import StructuralValidator
from backend.paper_fill_engine.validation.consistency import ConsistencyValidator
from backend.paper_fill_engine.core.stages import DeterministicFillStage, LifecycleValidationStage
from backend.paper_fill_engine.exceptions.exceptions import PaperFillValidationError, PaperFillConsistencyError
from backend.paper_fill_engine.models.fill import FillState

@pytest.fixture
def engine():
    repo = MemoryPaperFillRepository()
    mock_consistency = ConsistencyValidator()
    # Mocking validate to return a passed report
    from backend.paper_fill_engine.validation.models import ValidationReport
    mock_report = ValidationReport()
    mock_consistency.validate = AsyncMock(return_value=mock_report)
    
    return PaperFillEngine(
        repository=repo,
        structural_validator=StructuralValidator(),
        consistency_validator=mock_consistency,
        deterministic_fill_stage=DeterministicFillStage(),
        lifecycle_validation_stage=LifecycleValidationStage(),
        snapshot_builder=PaperFillSnapshotBuilder()
    )

@pytest.mark.asyncio
async def test_engine_flow_success(engine, dummy_context):
    snapshot = await engine.execute(dummy_context)
    
    assert snapshot is not None
    assert engine._repository.load(snapshot.snapshot_id) == snapshot
    assert snapshot.fill_state == FillState.PENDING_FILL

@pytest.mark.asyncio
async def test_engine_structural_failure(engine, dummy_metadata):
    from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext
    bad_context = PaperFillExecutionContext(
        symbol="",
        timeframe="1D",
        dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100},
        metadata=dummy_metadata
    )
    with pytest.raises(PaperFillValidationError):
        await engine.execute(bad_context)

@pytest.mark.asyncio
async def test_engine_consistency_failure(engine, dummy_context):
    from backend.paper_fill_engine.validation.models import ValidationReport
    mock_report = ValidationReport(passed=False, errors=["Consistency Error"])
    engine._consistency_validator.validate = AsyncMock(return_value=mock_report)
    
    with pytest.raises(PaperFillConsistencyError):
        await engine.execute(dummy_context)

@pytest.mark.asyncio
async def test_engine_propagates_warnings(dummy_context):
    # We must explicitly verify that the warnings are populated correctly
    # Since the Snapshot doesn't persist warnings, we mock the builder to capture the context
    mock_builder = MagicMock()
    mock_snapshot = MagicMock()
    mock_snapshot.business_fingerprint = "fp"
    mock_snapshot.snapshot_version = "v1"
    mock_snapshot.fill_state.value = "PENDING_FILL"
    mock_builder.build.return_value = mock_snapshot
    
    mock_structural = MagicMock()
    from backend.paper_fill_engine.validation.models import ValidationReport
    mock_report_structural = ValidationReport(passed=True, warnings=["Struct Warning"])
    mock_structural.validate.return_value = mock_report_structural
    
    mock_consistency = MagicMock()
    mock_report_consistency = ValidationReport(passed=True, warnings=["Consist Warning"])
    mock_consistency.validate = AsyncMock(return_value=mock_report_consistency)
    
    engine = PaperFillEngine(
        repository=MemoryPaperFillRepository(),
        structural_validator=mock_structural,
        consistency_validator=mock_consistency,
        deterministic_fill_stage=DeterministicFillStage(),
        lifecycle_validation_stage=LifecycleValidationStage(),
        snapshot_builder=mock_builder
    )
    
    await engine.execute(dummy_context)
    
    args, kwargs = mock_builder.build.call_args
    pipeline_context = args[1]
    
    assert "Struct Warning" in pipeline_context.diagnostics.warnings
    assert "Consist Warning" in pipeline_context.diagnostics.warnings
