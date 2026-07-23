from typing import Optional, List
from backend.paper_execution_quality_engine.contracts.repository import IPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot

class PostgreSQLPaperExecutionQualityRepository(IPaperExecutionQualityRepository):
    """
    PostgreSQL INSERT-only repository for paper execution quality snapshots.
    """
    def save(self, snapshot: PaperExecutionQualitySnapshot) -> None:
        raise NotImplementedError("PostgreSQL repository is not yet implemented.")

    def load(self, snapshot_id: str) -> Optional[PaperExecutionQualitySnapshot]:
        raise NotImplementedError("PostgreSQL repository is not yet implemented.")

    def exists(self, snapshot_id: str) -> bool:
        raise NotImplementedError("PostgreSQL repository is not yet implemented.")

    def load_latest(self) -> Optional[PaperExecutionQualitySnapshot]:
        raise NotImplementedError("PostgreSQL repository is not yet implemented.")
        
    def query_by_parent_fill_snapshot(self, version: str) -> List[PaperExecutionQualitySnapshot]:
        raise NotImplementedError("PostgreSQL repository is not yet implemented.")
