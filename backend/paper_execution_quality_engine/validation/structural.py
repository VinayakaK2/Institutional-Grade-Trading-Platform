from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext
from backend.paper_execution_quality_engine.validation.models import ValidationReport

class StructuralValidator:
    """
    Validates structural integrity of the PaperExecutionQualityExecutionContext.
    """
    def validate(self, context: PaperExecutionQualityExecutionContext) -> ValidationReport:
        report = ValidationReport()

        if not context.symbol:
            report.add_error("Symbol cannot be empty.")
            
        if not context.timeframe:
            report.add_error("Timeframe cannot be empty.")
            
        if not context.dataset_version:
            report.add_error("Dataset version cannot be empty.")
            
        if not context.parent_snapshot_references.parent_fill_snapshot_version:
            report.add_error("Parent fill snapshot version cannot be empty.")
            
        if not context.configuration_hash:
            report.add_error("Configuration hash cannot be empty.")
            
        if not context.execution_quality_model_version:
            report.add_error("Execution quality model version cannot be empty.")
            
        if not isinstance(context.configuration, dict):
            report.add_error("Configuration must be a dictionary.")

        return report
