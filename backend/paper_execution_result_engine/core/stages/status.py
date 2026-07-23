from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultPipelineContext
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus
from backend.paper_order_engine.models.order import OrderState
from backend.paper_fill_engine.models.fill import FillState

class ExecutionStatusStage:
    """
    Deterministically evaluates ExecutionStatus from upstream states.
    Validates business invariants implicitly since StructuralValidator 
    already verified basic bounds.
    """
    def execute(self, context: PaperExecutionResultPipelineContext) -> None:
        order_state = context.execution_context.paper_order_snapshot.order_state
        fill_state = context.execution_context.paper_fill_snapshot.fill_state
        
        req_qty = context.execution_context.metadata.get("requested_quantity", 0)
        filled_qty = context.execution_context.paper_fill_snapshot.total_filled_quantity
        
        # Precedence: Rejected -> Cancelled -> Expired -> Executed -> Partial
        
        if order_state == OrderState.REJECTED:
            context.execution_status = ExecutionStatus.REJECTED
            return
            
        if order_state == OrderState.CANCELLED:
            context.execution_status = ExecutionStatus.CANCELLED
            return
            
        if order_state == OrderState.EXPIRED or fill_state == FillState.EXPIRED:
            context.execution_status = ExecutionStatus.EXPIRED
            return
            
        if filled_qty == req_qty and filled_qty > 0:
            context.execution_status = ExecutionStatus.EXECUTED
            return
            
        if filled_qty > 0 and filled_qty < req_qty:
            context.execution_status = ExecutionStatus.PARTIALLY_EXECUTED
            return
            
        # Fallback for empty fills not covered by terminal order states
        from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError
        raise PaperExecutionResultCalculationError(
            f"Unable to resolve execution status. Order state: {order_state}, Fill state: {fill_state}, Filled: {filled_qty}, Requested: {req_qty}"
        )
