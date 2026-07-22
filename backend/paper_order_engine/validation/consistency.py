from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext
from backend.paper_order_engine.validation.models import ValidationReport
from backend.paper_execution_engine.contracts.repository import IPaperExecutionRepository

class ConsistencyValidator:
    """
    Validates logical consistency, such as verifying parent lineage.
    """
    def __init__(self, paper_execution_repository: IPaperExecutionRepository = None):
        self._paper_execution_repository = paper_execution_repository

    async def validate(self, context: PaperOrderExecutionContext) -> ValidationReport:
        report = ValidationReport()
        
        if self._paper_execution_repository:
            try:
                parent_pe_version = context.parent_paper_execution_snapshot_version
                
                # Check if the parent paper execution snapshot actually exists
                # Assuming IPaperExecutionRepository has load_by_snapshot_version
                exists = await self._paper_execution_repository.load_by_snapshot_version(parent_pe_version) is not None
                if not exists:
                    report.add_error(f"Parent paper execution snapshot {parent_pe_version} does not exist.")
            except Exception as e:
                report.add_error(f"Error validating consistency: {str(e)}")

        return report
