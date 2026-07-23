from typing import List, Optional
from backend.paper_execution_result_engine.contracts.repository import PaperExecutionResultRepository
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus

class PaperExecutionResultQueryService:
    """
    Provides query capabilities over the execution result repository.
    """
    def __init__(self, repository: PaperExecutionResultRepository):
        self._repository = repository
        
    def query_by_snapshot_version(self, version: str) -> Optional[PaperExecutionSnapshot]:
        if self._repository.exists(version):
            return self._repository.load(version)
        return None
        
    def query_by_status(self, status: ExecutionStatus) -> List[PaperExecutionSnapshot]:
        return [s for s in self._repository.list_all() if s.execution_status == status]
        
    def query_by_parent_order_snapshot(self, order_snapshot_version: str) -> List[PaperExecutionSnapshot]:
        return [s for s in self._repository.list_all() if s.parent_order_snapshot_version == order_snapshot_version]
        
    def query_by_parent_fill_snapshot(self, fill_snapshot_version: str) -> List[PaperExecutionSnapshot]:
        return [s for s in self._repository.list_all() if s.parent_fill_snapshot_version == fill_snapshot_version]
        
    def query_by_symbol(self, symbol: str) -> List[PaperExecutionSnapshot]:
        return [s for s in self._repository.list_all() if s.metadata.get("symbol") == symbol]
        
    def query_by_timeframe(self, start_iso: str, end_iso: str) -> List[PaperExecutionSnapshot]:
        return [s for s in self._repository.list_all() if start_iso <= s.created_at.isoformat() <= end_iso]
