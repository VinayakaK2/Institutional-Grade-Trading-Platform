from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultValidationError

class ConsistencyValidator:
    """
    Validates snapshot lineage matching across all upstream components.
    """
    @staticmethod
    def validate(context: PaperExecutionResultExecutionContext) -> None:
        dec_version = context.portfolio_decision_snapshot.snapshot_id
        order_parent_dec_version = context.paper_order_snapshot.parent_portfolio_decision_snapshot_version
        
        if order_parent_dec_version != dec_version:
            raise PaperExecutionResultValidationError(
                f"Lineage mismatch: Order's parent decision '{order_parent_dec_version}' "
                f"does not match actual Decision snapshot '{dec_version}'."
            )
            
        order_version = context.paper_order_snapshot.snapshot_version
        fill_parent_order_version = context.paper_fill_snapshot.parent_paper_order_snapshot_version
        
        if fill_parent_order_version != order_version:
            raise PaperExecutionResultValidationError(
                f"Lineage mismatch: Fill's parent order '{fill_parent_order_version}' "
                f"does not match actual Order snapshot '{order_version}'."
            )
            
        fill_version = context.paper_fill_snapshot.snapshot_version
        eq_parent_fill_version = context.paper_execution_quality_snapshot.parent_fill_snapshot_version
        
        if eq_parent_fill_version != fill_version:
            raise PaperExecutionResultValidationError(
                f"Lineage mismatch: Execution Quality's parent fill '{eq_parent_fill_version}' "
                f"does not match actual Fill snapshot '{fill_version}'."
            )
