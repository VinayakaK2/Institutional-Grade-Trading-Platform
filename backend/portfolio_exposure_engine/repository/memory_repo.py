import asyncio
import copy
from typing import Dict, Optional
from backend.portfolio_exposure_engine.contracts.repository import IPortfolioExposureRepository
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_exposure_engine.exceptions import PortfolioExposureRepositoryError

class MemoryPortfolioExposureRepository(IPortfolioExposureRepository):
    """
    In-memory INSERT-only implementation of the Portfolio Exposure Repository.
    """
    def __init__(self):
        self._store: Dict[str, PortfolioExposureSnapshot] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, snapshot: PortfolioExposureSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_id in self._store:
                raise PortfolioExposureRepositoryError(f"Snapshot {snapshot.snapshot_id} already exists. Updates are strictly forbidden.")
            self._store[snapshot.snapshot_id] = copy.deepcopy(snapshot)
            
    async def load(self, snapshot_id: str) -> PortfolioExposureSnapshot:
        async with self._lock:
            if snapshot_id not in self._store:
                raise KeyError(f"Snapshot {snapshot_id} not found.")
            return copy.deepcopy(self._store[snapshot_id])
            
    async def exists(self, snapshot_id: str) -> bool:
        async with self._lock:
            return snapshot_id in self._store
            
    async def latest(self) -> Optional[PortfolioExposureSnapshot]:
        async with self._lock:
            if not self._store:
                return None
            sorted_snapshots = sorted(self._store.values(), key=lambda s: s.created_at)
            return copy.deepcopy(sorted_snapshots[-1])
