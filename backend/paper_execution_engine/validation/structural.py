from backend.paper_execution_engine.models.contexts import PaperExecutionContext
from backend.paper_execution_engine.validation.models import ValidationReport

class StructuralValidator:
    """
    Validates the structural correctness of the execution context.
    """
    
    def validate(self, context: PaperExecutionContext) -> ValidationReport:
        report = ValidationReport(passed=True)
        
        if not context.symbol:
            report.add_error("Symbol cannot be empty.")
            
        if not context.timeframe:
            report.add_error("Timeframe cannot be empty.")
            
        if not context.dataset_version:
            report.add_error("Dataset version cannot be empty.")
            
        if not context.parent_portfolio_decision_snapshot_version:
            report.add_error("Parent portfolio decision snapshot version cannot be empty.")
            
        if not context.configuration:
            report.add_error("Configuration cannot be null.")
        else:
            if not context.configuration.engine_version:
                report.add_error("Configuration engine_version cannot be empty.")
            if not context.configuration.snapshot_version:
                report.add_error("Configuration snapshot_version cannot be empty.")
                
        if not context.metadata:
            report.add_error("Metadata cannot be null.")
            
        return report
