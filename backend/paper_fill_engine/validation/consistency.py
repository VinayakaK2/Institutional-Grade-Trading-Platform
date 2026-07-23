from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext
from backend.paper_fill_engine.validation.models import ValidationReport
from backend.paper_order_engine.contracts.repository import IPaperOrderRepository
from backend.paper_order_engine.models.order import OrderState

class ConsistencyValidator:
    """
    Validates logical consistency, such as verifying parent lineage and order status.
    """
    def __init__(self, paper_order_repository: IPaperOrderRepository = None):
        self._paper_order_repository = paper_order_repository

    async def validate(self, context: PaperFillExecutionContext) -> ValidationReport:
        report = ValidationReport()
        
        if self._paper_order_repository:
            try:
                parent_version = context.parent_paper_order_snapshot_version
                
                # Check if the parent paper order snapshot actually exists
                parent_snapshot = self._paper_order_repository.load_by_snapshot_version(parent_version)
                if not parent_snapshot:
                    report.add_error(f"Parent paper order snapshot {parent_version} does not exist.")
                else:
                    if parent_snapshot.order_state != OrderState.ACCEPTED:
                        report.add_error(f"Order must be ACCEPTED to simulate fills. Current state: {parent_snapshot.order_state.value}")
                        
            except Exception as e:
                report.add_error(f"Error validating consistency: {str(e)}")

        return report
