from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultValidationError

class StructuralValidator:
    """
    Validates structural business invariants BEFORE resolution stages run.
    """
    @staticmethod
    def validate(context: PaperExecutionResultExecutionContext) -> None:
        try:
            # Check for missing snapshots (Pydantic already enforces type/presence, but we double-check)
            if not context.portfolio_decision_snapshot:
                raise PaperExecutionResultValidationError("Missing portfolio decision snapshot.")
            if not context.paper_order_snapshot:
                raise PaperExecutionResultValidationError("Missing paper order snapshot.")
            if not context.paper_fill_snapshot:
                raise PaperExecutionResultValidationError("Missing paper fill snapshot.")
            if not context.paper_execution_quality_snapshot:
                raise PaperExecutionResultValidationError("Missing paper execution quality snapshot.")
            
            # Using metadata requested_quantity
            requested_qty = context.metadata.get("requested_quantity", 0)
            filled_qty = context.paper_fill_snapshot.total_filled_quantity
            remaining_qty = context.paper_fill_snapshot.remaining_quantity
            
            # Business invariants
            if filled_qty > requested_qty:
                raise PaperExecutionResultValidationError(f"Filled quantity ({filled_qty}) cannot exceed requested quantity ({requested_qty}).")
            if remaining_qty < 0:
                raise PaperExecutionResultValidationError(f"Remaining quantity ({remaining_qty}) cannot be negative.")
            if filled_qty + remaining_qty != requested_qty:
                raise PaperExecutionResultValidationError(f"Filled ({filled_qty}) + Remaining ({remaining_qty}) must equal Requested ({requested_qty}).")
            
            if context.paper_fill_snapshot.average_fill_price is not None and context.paper_fill_snapshot.average_fill_price < 0:
                raise PaperExecutionResultValidationError("Average fill price cannot be negative.")
                
            eq_report = context.paper_execution_quality_snapshot.execution_quality_report
            if eq_report.market_impact.impact_cost < 0:
                raise PaperExecutionResultValidationError("Execution cost cannot be negative.")
                
            # Timeline timestamps monotonic check
            events = context.paper_fill_snapshot.fill_events
            for i in range(1, len(events)):
                if events[i].timestamp < events[i-1].timestamp:
                    raise PaperExecutionResultValidationError("Fill events must be chronologically ordered (monotonic timestamps).")
                    
        except AttributeError as e:
            raise PaperExecutionResultValidationError(f"Structural validation failed due to missing required field: {str(e)}")
