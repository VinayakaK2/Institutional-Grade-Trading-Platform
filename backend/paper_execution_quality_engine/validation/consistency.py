from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext
from backend.paper_execution_quality_engine.validation.models import ValidationReport
from backend.paper_fill_engine.contracts.repository import IPaperFillRepository

class ConsistencyValidator:
    """
    Validates logical consistency, such as verifying parent fill lineage exists.
    """
    def __init__(self, paper_fill_repository: IPaperFillRepository = None):
        self._paper_fill_repository = paper_fill_repository

    async def validate(self, context: PaperExecutionQualityExecutionContext) -> ValidationReport:
        report = ValidationReport()
        
        if self._paper_fill_repository:
            try:
                parent_version = context.parent_snapshot_references.parent_fill_snapshot_version
                
                parent_snapshot = self._paper_fill_repository.load(parent_version)
                if not parent_snapshot:
                    report.add_error(f"Parent paper fill snapshot {parent_version} does not exist.")
                        
            except Exception as e:
                report.add_error(f"Error validating consistency: {str(e)}")

        return report
