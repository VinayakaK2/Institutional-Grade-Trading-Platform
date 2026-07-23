from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultPipelineContext
from backend.paper_execution_result_engine.models.resolution import ExecutionSummary

class ExecutionSummaryStage:
    """
    Aggregates quantity and execution cost without recalculating pricing.
    """
    def execute(self, context: PaperExecutionResultPipelineContext) -> None:
        fill_snapshot = context.execution_context.paper_fill_snapshot
        eq_snapshot = context.execution_context.paper_execution_quality_snapshot
        status = context.execution_status
        
        if not status:
            from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError
            raise PaperExecutionResultCalculationError("ExecutionStatus must be resolved before ExecutionSummary.")

        summary = ExecutionSummary(
            requested_quantity=context.execution_context.metadata.get("requested_quantity", 0),
            filled_quantity=fill_snapshot.total_filled_quantity,
            remaining_quantity=fill_snapshot.remaining_quantity,
            fill_count=len(fill_snapshot.fill_events),
            average_fill_price=fill_snapshot.average_fill_price,
            execution_cost=eq_snapshot.execution_quality_report.market_impact.impact_cost,
            total_slippage=eq_snapshot.execution_quality_report.slippage.slippage_amount,
            total_market_impact=eq_snapshot.execution_quality_report.market_impact.market_impact,
            total_spread_cost=eq_snapshot.execution_quality_report.spread_cost.paid_spread,
            execution_status=status
        )
        
        context.execution_summary = summary
