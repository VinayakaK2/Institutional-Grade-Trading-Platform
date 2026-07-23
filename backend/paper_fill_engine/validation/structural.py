from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext
from backend.paper_fill_engine.validation.models import ValidationReport

class StructuralValidator:
    """
    Validates structural integrity of the PaperFillExecutionContext.
    """
    def validate(self, context: PaperFillExecutionContext) -> ValidationReport:
        report = ValidationReport()

        if not context.symbol:
            report.add_error("Symbol cannot be empty.")
            
        if not context.timeframe:
            report.add_error("Timeframe cannot be empty.")
            
        if not context.dataset_version:
            report.add_error("Dataset version cannot be empty.")
            
        if not context.parent_paper_order_snapshot_version:
            report.add_error("Parent paper order snapshot version cannot be empty.")
            
        if not isinstance(context.configuration, dict):
            report.add_error("Configuration must be a dictionary.")

        return report
