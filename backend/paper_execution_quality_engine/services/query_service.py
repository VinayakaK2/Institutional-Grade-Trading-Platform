from typing import List
from backend.paper_execution_quality_engine.contracts.repository import IPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot

class PaperExecutionQualityQueryService:
    """
    CQRS Query Service for Paper Execution Quality Snapshots.
    """
    def __init__(self, repository: IPaperExecutionQualityRepository):
        self._repository = repository

    def query_by_parent_fill_snapshot(self, parent_version: str) -> List[PaperExecutionQualitySnapshot]:
        return self._repository.query_by_parent_fill_snapshot(parent_version)
