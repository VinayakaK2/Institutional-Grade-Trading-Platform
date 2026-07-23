from typing import Optional
from backend.paper_execution_optimization_engine.contracts.repository import IPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot


class PaperExecutionOptimizationQueryService:
    """
    Query service for optimization snapshots. Read-only.
    Uses optimization-centric keys only.
    """
    
    def __init__(self, repository: IPaperExecutionOptimizationRepository):
        self._repository = repository
        
    async def query_by_fingerprint(self, optimization_fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        """
        Loads an optimization snapshot by its fingerprint.
        """
        return await self._repository.load(optimization_fingerprint)
        
    async def query_latest(self) -> Optional[PaperExecutionOptimizationSnapshot]:
        """
        Loads the most recently saved snapshot, if any.
        """
        return await self._repository.load_latest()
