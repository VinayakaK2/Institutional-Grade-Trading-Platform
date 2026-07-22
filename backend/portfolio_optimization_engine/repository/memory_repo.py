from typing import Optional, Dict
from backend.portfolio_optimization_engine.contracts.repository import IPortfolioOptimizationRepository
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot

class MemoryPortfolioOptimizationRepository(IPortfolioOptimizationRepository):
    """
    In-memory implementation of the repository for testing and fast local execution.
    """
    def __init__(self):
        self._store: Dict[str, PortfolioOptimizationSnapshot] = {}
        self._latest_id: Optional[str] = None
        
    async def save(self, snapshot: PortfolioOptimizationSnapshot) -> None:
        if await self.exists(snapshot.snapshot_id):
            raise ValueError(f"Snapshot {snapshot.snapshot_id} already exists (Immutability violation).")
        self._store[snapshot.snapshot_id] = snapshot
        self._latest_id = snapshot.snapshot_id
        
    async def load(self, snapshot_id: str) -> Optional[PortfolioOptimizationSnapshot]:
        return self._store.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._store
        
    async def load_latest(self) -> Optional[PortfolioOptimizationSnapshot]:
        if self._latest_id:
            return self._store.get(self._latest_id)
        return None
