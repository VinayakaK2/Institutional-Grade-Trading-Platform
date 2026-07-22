import pytest
from unittest.mock import AsyncMock
from backend.paper_order_engine.validation.structural import StructuralValidator
from backend.paper_order_engine.validation.consistency import ConsistencyValidator
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext
from backend.paper_order_engine.models.order import OrderType

def test_structural_validation_pass(dummy_context):
    validator = StructuralValidator()
    report = validator.validate(dummy_context)
    assert report.passed is True
    assert len(report.errors) == 0

def test_structural_validation_invalid_order_type(dummy_metadata):
    context = PaperOrderExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration={"order_type": "UNKNOWN"},
        metadata=dummy_metadata
    )
    validator = StructuralValidator()
    report = validator.validate(context)
    assert report.passed is False
    assert any("Invalid order_type" in e for e in report.errors)

def test_structural_validation_limit_missing_price(dummy_metadata):
    context = PaperOrderExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration={"order_type": OrderType.LIMIT.value},
        metadata=dummy_metadata
    )
    validator = StructuralValidator()
    report = validator.validate(context)
    assert report.passed is False
    assert any("LIMIT order requires 'limit_price'" in e for e in report.errors)

def test_structural_validation_stop_missing_price(dummy_metadata):
    context = PaperOrderExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_dec_123",
        parent_paper_execution_snapshot_version="p_exec_123",
        configuration={"order_type": OrderType.STOP.value},
        metadata=dummy_metadata
    )
    validator = StructuralValidator()
    report = validator.validate(context)
    assert report.passed is False
    assert any("STOP order requires 'stop_price'" in e for e in report.errors)

@pytest.mark.asyncio
async def test_consistency_validation_pass(dummy_context):
    mock_repo = AsyncMock()
    mock_repo.load_by_snapshot_version.return_value = True
    
    validator = ConsistencyValidator(paper_execution_repository=mock_repo)
    report = await validator.validate(dummy_context)
    assert report.passed is True

@pytest.mark.asyncio
async def test_consistency_validation_missing_parent(dummy_context):
    mock_repo = AsyncMock()
    mock_repo.load_by_snapshot_version.return_value = None
    
    validator = ConsistencyValidator(paper_execution_repository=mock_repo)
    report = await validator.validate(dummy_context)
    
    assert report.passed is False
    assert any("does not exist" in e for e in report.errors)
