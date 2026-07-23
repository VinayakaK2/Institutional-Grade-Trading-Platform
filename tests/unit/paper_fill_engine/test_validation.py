import pytest
from unittest.mock import MagicMock
from backend.paper_fill_engine.validation.structural import StructuralValidator
from backend.paper_fill_engine.validation.consistency import ConsistencyValidator
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext
from backend.paper_order_engine.models.order import OrderState

def test_structural_validation_pass(dummy_context):
    validator = StructuralValidator()
    report = validator.validate(dummy_context)
    assert report.passed is True

def test_structural_validation_failures(dummy_metadata):
    context = PaperFillExecutionContext(
        symbol="",
        timeframe="1D",
        dataset_version="v1.0",
        parent_paper_order_snapshot_version="p_order_123",
        configuration={"requested_quantity": 100},
        metadata=dummy_metadata
    )
    validator = StructuralValidator()
    report = validator.validate(context)
    assert report.passed is False
    assert any("Symbol cannot be empty" in e for e in report.errors)

@pytest.mark.asyncio
async def test_consistency_validation_pass(dummy_context):
    mock_repo = MagicMock()
    mock_snapshot = MagicMock()
    mock_snapshot.order_state = OrderState.ACCEPTED
    mock_repo.load_by_snapshot_version.return_value = mock_snapshot
    
    validator = ConsistencyValidator(paper_order_repository=mock_repo)
    report = await validator.validate(dummy_context)
    assert report.passed is True

@pytest.mark.asyncio
async def test_consistency_validation_missing_parent(dummy_context):
    mock_repo = MagicMock()
    mock_repo.load_by_snapshot_version.return_value = None
    
    validator = ConsistencyValidator(paper_order_repository=mock_repo)
    report = await validator.validate(dummy_context)
    assert report.passed is False
    assert any("does not exist" in e for e in report.errors)

@pytest.mark.asyncio
async def test_consistency_validation_not_accepted(dummy_context):
    mock_repo = MagicMock()
    mock_snapshot = MagicMock()
    mock_snapshot.order_state = OrderState.CREATED
    mock_repo.load_by_snapshot_version.return_value = mock_snapshot
    
    validator = ConsistencyValidator(paper_order_repository=mock_repo)
    report = await validator.validate(dummy_context)
    assert report.passed is False
    assert any("Order must be ACCEPTED" in e for e in report.errors)
