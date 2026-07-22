import asyncio
import copy
from typing import Dict
from backend.portfolio_engine.contracts.repository import IPortfolioRepository
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot
from backend.portfolio_engine.exceptions import PortfolioRepositoryError

class MemoryPortfolioRepository(IPortfolioRepository):
    """
    In-memory INSERT-only implementation of the Portfolio Repository.
    Guarantees Atomic Save OR No Save.
    """
    def __init__(self):
        self._store: Dict[str, PortfolioSnapshot] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, snapshot: PortfolioSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_id in self._store:
                raise PortfolioRepositoryError(f"Snapshot {snapshot.snapshot_id} already exists. Updates are strictly forbidden.")
            # Atomic save via deepcopy to prevent mutable state leakage
            self._store[snapshot.snapshot_id] = copy.deepcopy(snapshot)
            
    async def load(self, snapshot_id: str) -> PortfolioSnapshot:
        async with self._lock:
            if snapshot_id not in self._store:
                raise KeyError(f"Snapshot {snapshot_id} not found.")
            return copy.deepcopy(self._store[snapshot_id])
            
    async def exists(self, snapshot_id: str) -> bool:
        async with self._lock:
            return snapshot_id in self._store
