import pytest
from unittest.mock import MagicMock
from backend.paper_execution_engine.validation.structural import StructuralValidator
from backend.paper_execution_engine.validation.consistency import ConsistencyValidator
from backend.paper_execution_engine.models.contexts import (
    PaperExecutionContext
)

def test_structural_validation_pass(dummy_context):
    validator = StructuralValidator()
    report = validator.validate(dummy_context)
    assert report.passed is True
    assert len(report.errors) == 0

def test_structural_validation_missing_symbol(dummy_configuration, dummy_metadata):
    context = PaperExecutionContext(
        symbol="",
        timeframe="1D",
        dataset_version="v1.0",
        parent_portfolio_decision_snapshot_version="p_v_123",
        configuration=dummy_configuration,
        metadata=dummy_metadata
    )
    validator = StructuralValidator()
    report = validator.validate(context)
    assert report.passed is False
    assert "Symbol cannot be empty." in report.errors

@pytest.mark.asyncio
async def test_consistency_validation_pass(dummy_context):
    # Without external repo, it should pass
    validator = ConsistencyValidator()
    report = await validator.validate(dummy_context)
    assert report.passed is True

@pytest.mark.asyncio
async def test_consistency_validation_missing_parent(dummy_context):
    mock_repo = MagicMock()
    mock_repo.exists.return_value = False
    
    validator = ConsistencyValidator(portfolio_decision_repository=mock_repo)
    report = await validator.validate(dummy_context)
    
    assert report.passed is False
    assert "Parent portfolio decision snapshot p_v_123 does not exist." in report.errors
