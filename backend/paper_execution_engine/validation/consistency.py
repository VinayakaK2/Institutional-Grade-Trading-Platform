from backend.paper_execution_engine.models.contexts import PaperExecutionContext
from backend.paper_execution_engine.validation.models import ValidationReport
from backend.portfolio_decision_engine.contracts.repository import IPortfolioDecisionRepository

class ConsistencyValidator:
    """
    Validates the consistency of the execution context, particularly cross-referencing
    parent snapshots and datasets if necessary.
    """
    
    def __init__(self, portfolio_decision_repository: IPortfolioDecisionRepository = None):
        self._portfolio_decision_repository = portfolio_decision_repository
        
    async def validate(self, context: PaperExecutionContext) -> ValidationReport:
        report = ValidationReport(passed=True)
        
        # Check lineage consistency if repository provided
        if self._portfolio_decision_repository:
            try:
                parent_version = context.parent_portfolio_decision_snapshot_version
                # Usually we would load the parent snapshot to verify it exists and matches
                exists = self._portfolio_decision_repository.exists(parent_version)
                if not exists:
                    report.add_error(f"Parent portfolio decision snapshot {parent_version} does not exist.")
            except Exception as e:
                report.add_warning(f"Could not verify parent snapshot consistency: {str(e)}")
                
        # In this foundation phase, consistency checks might be simple.
        # Future phases will add more consistency validation logic.
        
        return report
