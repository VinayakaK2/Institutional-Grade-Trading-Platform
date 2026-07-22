import copy
from typing import List, Optional
from backend.portfolio_state_engine.contracts.query_service import IPortfolioStateQueryService
from backend.portfolio_state_engine.repository.memory_repo import MemoryPortfolioStateRepository
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot

class MemoryPortfolioStateQueryService(IPortfolioStateQueryService):
    """
    In-memory projection-oriented read service.
    Answers historical and current state queries.
    """
    def __init__(self, repository: MemoryPortfolioStateRepository):
        self._repository = repository
        
    async def get_latest_state(self) -> Optional[PortfolioStateSnapshot]:
        return await self._repository.latest()
        
    async def get_history(self) -> List[PortfolioStateSnapshot]:
        async with self._repository._lock:
            # Sort by creation time to ensure consistent ordering
            sorted_snapshots = sorted(self._repository._store.values(), key=lambda s: s.created_at)
            return [copy.deepcopy(s) for s in sorted_snapshots]
