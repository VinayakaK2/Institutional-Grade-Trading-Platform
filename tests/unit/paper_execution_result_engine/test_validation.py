import pytest
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultValidationError
from backend.paper_execution_result_engine.validation.structural import StructuralValidator
from backend.paper_execution_result_engine.validation.consistency import ConsistencyValidator

def test_structural_validation_success(mock_execution_context):
    StructuralValidator.validate(mock_execution_context)

def test_structural_validation_overfill(mock_execution_context):
    bad_fill = mock_execution_context.paper_fill_snapshot.model_copy(update={"total_filled_quantity": 150, "remaining_quantity": -50})
    context = mock_execution_context.model_copy(update={"paper_fill_snapshot": bad_fill})
    with pytest.raises(PaperExecutionResultValidationError, match="cannot exceed requested"):
        StructuralValidator.validate(context)

def test_structural_validation_negative_remaining(mock_execution_context):
    bad_fill = mock_execution_context.paper_fill_snapshot.model_copy(update={"total_filled_quantity": 100, "remaining_quantity": -10})
    context = mock_execution_context.model_copy(update={"paper_fill_snapshot": bad_fill})
    with pytest.raises(PaperExecutionResultValidationError, match="cannot be negative"):
        StructuralValidator.validate(context)

def test_consistency_validation_success(mock_execution_context):
    ConsistencyValidator.validate(mock_execution_context)

def test_consistency_validation_mismatch(mock_execution_context):
    bad_order = mock_execution_context.paper_order_snapshot.model_copy(update={"parent_portfolio_decision_snapshot_version": "wrong"})
    context = mock_execution_context.model_copy(update={"paper_order_snapshot": bad_order})
    with pytest.raises(PaperExecutionResultValidationError, match="Lineage mismatch"):
        ConsistencyValidator.validate(context)
