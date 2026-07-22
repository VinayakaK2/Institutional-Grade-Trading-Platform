from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext
from backend.paper_order_engine.validation.models import ValidationReport
from backend.paper_order_engine.models.order import OrderType

class StructuralValidator:
    """
    Validates structural integrity of the PaperOrderExecutionContext.
    """
    def validate(self, context: PaperOrderExecutionContext) -> ValidationReport:
        report = ValidationReport()

        if not context.symbol:
            report.add_error("Symbol cannot be empty.")
            
        if not context.timeframe:
            report.add_error("Timeframe cannot be empty.")
            
        if not context.dataset_version:
            report.add_error("Dataset version cannot be empty.")
            
        if not context.parent_portfolio_decision_snapshot_version:
            report.add_error("Parent portfolio decision snapshot version cannot be empty.")
            
        if not context.parent_paper_execution_snapshot_version:
            report.add_error("Parent paper execution snapshot version cannot be empty.")
            
        if "order_type" not in context.configuration:
            report.add_error("Configuration missing 'order_type'.")
        else:
            try:
                OrderType(context.configuration["order_type"])
            except ValueError:
                report.add_error(f"Invalid order_type: {context.configuration['order_type']}. Must be MARKET, LIMIT, or STOP.")
                
        # Limit/Stop order validation
        order_type = context.configuration.get("order_type")
        if order_type == OrderType.LIMIT.value and "limit_price" not in context.configuration:
            report.add_error("LIMIT order requires 'limit_price' in configuration.")
        if order_type == OrderType.STOP.value and "stop_price" not in context.configuration:
            report.add_error("STOP order requires 'stop_price' in configuration.")

        return report
