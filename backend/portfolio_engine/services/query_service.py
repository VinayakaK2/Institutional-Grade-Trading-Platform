import copy
from typing import List, Optional
from backend.portfolio_engine.contracts.query_service import IPortfolioQueryService
from backend.portfolio_engine.repository.memory_repo import MemoryPortfolioRepository
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot

class MemoryQueryService(IPortfolioQueryService):
    """
    In-memory projection-oriented read service.
    """
    def __init__(self, repository: MemoryPortfolioRepository):
        self._repository = repository
        
    async def load_latest_snapshot(self, symbol: str, timeframe: str) -> Optional[PortfolioSnapshot]:
        # Implementation depends on how the repository is structured internally.
        # For this in-memory mock, we'll scan and find the latest.
        latest = None
        
        async with self._repository._lock:
            for snapshot in self._repository._store.values():
                # Note: PortfolioSnapshot doesn't have symbol/timeframe directly on it, 
                # but in a real database, it would be indexed.
                # For this implementation, we will assume it is in the metadata for querying purposes.
                meta = snapshot.metadata
                if meta.get('symbol') == symbol and meta.get('timeframe') == timeframe:
                    if latest is None or snapshot.created_at > latest.created_at:
                        latest = snapshot
                        
        return copy.deepcopy(latest) if latest else None
        
    async def load_snapshot_lineage(self, parent_risk_snapshot_version: str) -> List[PortfolioSnapshot]:
        lineage = []
        async with self._repository._lock:
            for snapshot in self._repository._store.values():
                if snapshot.parent_snapshot_references.risk_snapshot_version == parent_risk_snapshot_version:
                    lineage.append(copy.deepcopy(snapshot))
                    
        # Sort by creation time to ensure consistent ordering
        lineage.sort(key=lambda s: s.created_at)
        return lineage
