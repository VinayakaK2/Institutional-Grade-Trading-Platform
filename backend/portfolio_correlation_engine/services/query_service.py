import copy
from typing import List, Optional
from backend.portfolio_correlation_engine.contracts.query_service import IPortfolioCorrelationQueryService
from backend.portfolio_correlation_engine.repository.memory_repo import MemoryPortfolioCorrelationRepository
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot

class MemoryPortfolioCorrelationQueryService(IPortfolioCorrelationQueryService):
    """
    In-memory projection-oriented read service.
    """
    def __init__(self, repository: MemoryPortfolioCorrelationRepository):
        self._repository = repository
        
    async def get_latest_correlation(self) -> Optional[PortfolioCorrelationSnapshot]:
        return await self._repository.latest()
        
    async def get_history(self) -> List[PortfolioCorrelationSnapshot]:
        async with self._repository._lock:
            sorted_snapshots = sorted(self._repository._store.values(), key=lambda s: s.created_at)
            return [copy.deepcopy(s) for s in sorted_snapshots]
            
    async def query_by_symbol(self, symbol: str) -> List[PortfolioCorrelationSnapshot]:
        async with self._repository._lock:
            # Filters snapshots where the symbol matches the candidate symbol
            results = []
            for s in self._repository._store.values():
                # We don't have candidate symbol directly in snapshot but we could add it to metadata or analysis
                # For now, we assume metadata contains candidate_symbol
                if s.metadata.get("candidate_symbol") == symbol:
                    results.append(s)
            sorted_snapshots = sorted(results, key=lambda s: s.created_at)
            return [copy.deepcopy(s) for s in sorted_snapshots]
