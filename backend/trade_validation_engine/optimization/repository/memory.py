from typing import Optional, List, Dict
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot
from backend.trade_validation_engine.optimization.contracts.repository import IOptimizationRepository

class InMemoryOptimizationRepository(IOptimizationRepository):
    """
    In-memory implementation for testing and development.
    """
    def __init__(self) -> None:
        self._storage: Dict[str, OptimizationSnapshot] = {}

    async def save(self, snapshot: OptimizationSnapshot) -> None:
        if snapshot.optimization_id not in self._storage:
            self._storage[snapshot.optimization_id] = snapshot

    async def save_many(self, snapshots: List[OptimizationSnapshot]) -> None:
        for s in snapshots:
            await self.save(s)

    async def load(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        return self._storage.get(optimization_id)

    async def exists(self, optimization_id: str) -> bool:
        return optimization_id in self._storage

    async def load_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        # Return the first matching snapshot (latest run for this fingerprint)
        results = [s for s in self._storage.values() if s.business_fingerprint == fingerprint]
        if not results:
            return None
        return results[-1]
