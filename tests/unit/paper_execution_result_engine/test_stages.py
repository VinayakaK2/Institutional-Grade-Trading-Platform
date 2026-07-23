from backend.paper_execution_result_engine.core.stages.status import ExecutionStatusStage
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultPipelineContext
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus
from backend.paper_order_engine.models.order import OrderState
from backend.paper_fill_engine.models.fill import FillState
import pytest
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError

def test_status_stage_executed(mock_execution_context):
    context = PaperExecutionResultPipelineContext(execution_context=mock_execution_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.EXECUTED

def test_status_stage_rejected(mock_execution_context):
    bad_order = mock_execution_context.paper_order_snapshot.model_copy(update={"order_state": OrderState.REJECTED})
    exec_context = mock_execution_context.model_copy(update={"paper_order_snapshot": bad_order})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.REJECTED

def test_status_stage_cancelled(mock_execution_context):
    bad_order = mock_execution_context.paper_order_snapshot.model_copy(update={"order_state": OrderState.CANCELLED})
    exec_context = mock_execution_context.model_copy(update={"paper_order_snapshot": bad_order})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.CANCELLED

def test_status_stage_expired(mock_execution_context):
    bad_order = mock_execution_context.paper_order_snapshot.model_copy(update={"order_state": OrderState.EXPIRED})
    exec_context = mock_execution_context.model_copy(update={"paper_order_snapshot": bad_order})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.EXPIRED

def test_status_stage_fill_expired(mock_execution_context):
    bad_fill = mock_execution_context.paper_fill_snapshot.model_copy(update={"fill_state": FillState.EXPIRED})
    exec_context = mock_execution_context.model_copy(update={"paper_fill_snapshot": bad_fill})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.EXPIRED

def test_status_stage_partial(mock_execution_context):
    bad_fill = mock_execution_context.paper_fill_snapshot.model_copy(update={"total_filled_quantity": 50})
    exec_context = mock_execution_context.model_copy(update={"paper_fill_snapshot": bad_fill})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    ExecutionStatusStage().execute(context)
    assert context.execution_status == ExecutionStatus.PARTIALLY_EXECUTED

def test_status_stage_fallback(mock_execution_context):
    bad_fill = mock_execution_context.paper_fill_snapshot.model_copy(update={"total_filled_quantity": 0, "fill_state": FillState.PENDING_FILL})
    exec_context = mock_execution_context.model_copy(update={"paper_fill_snapshot": bad_fill})
    context = PaperExecutionResultPipelineContext(execution_context=exec_context)
    with pytest.raises(PaperExecutionResultCalculationError, match="Unable to resolve execution status"):
        ExecutionStatusStage().execute(context)
