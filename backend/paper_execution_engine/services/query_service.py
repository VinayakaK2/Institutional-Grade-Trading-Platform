from typing import List
from backend.paper_execution_engine.contracts.repository import IPaperExecutionRepository
from backend.paper_execution_engine.models.snapshot import PaperExecutionSnapshot

class PaperExecutionQueryService:
    """
    CQRS read-only endpoints for Paper Execution snapshots.
    """
    def __init__(self, repository: IPaperExecutionRepository):
        self._repository = repository
        
    async def query_by_symbol(self, symbol: str) -> List[PaperExecutionSnapshot]:
        # For a true DB repository, this would be a SQL query.
        # Here we mock it by loading the latest and checking symbol (in-memory simulation fallback if needed)
        # But wait, the repository interface doesn't expose list all.
        # We will assume future implementations of the repo could support this natively,
        # but the query service can expose the interface.
        raise NotImplementedError("query_by_symbol is not implemented in memory fallback yet")
        
    async def query_by_timeframe(self, timeframe: str) -> List[PaperExecutionSnapshot]:
        raise NotImplementedError("query_by_timeframe is not implemented")
        
    async def query_by_parent_portfolio_decision_snapshot(self, parent_version: str) -> List[PaperExecutionSnapshot]:
        raise NotImplementedError("query_by_parent_portfolio_decision_snapshot is not implemented")
        
    async def query_by_dataset_version(self, dataset_version: str) -> List[PaperExecutionSnapshot]:
        raise NotImplementedError("query_by_dataset_version is not implemented")
        
    async def query_latest(self) -> PaperExecutionSnapshot:
        return await self._repository.load_latest()
        
    async def query_by_snapshot_version(self, snapshot_version: str) -> PaperExecutionSnapshot:
        return await self._repository.load_by_snapshot_version(snapshot_version)
