from typing import Optional, List, Dict
from backend.liquidity_grab_engine.optimization.contracts.repository import IOptimizationRepository
from backend.liquidity_grab_engine.optimization.models.models import OptimizationSnapshot

class InMemoryOptimizationRepository(IOptimizationRepository):
    def __init__(self) -> None:
        self._snapshots: Dict[str, OptimizationSnapshot] = {}
        # Simple ordered list to track insertion order for load_latest
        self._ordered_ids: List[str] = []

    async def save(self, snapshot: OptimizationSnapshot) -> None:
        key = snapshot.business_fingerprint.fingerprint_hash
        if key not in self._snapshots:
            self._ordered_ids.append(key)
        self._snapshots[key] = snapshot
        
    async def exists(self, fingerprint_hash: str) -> bool:
        return fingerprint_hash in self._snapshots
        
    async def load(self, fingerprint_hash: str) -> Optional[OptimizationSnapshot]:
        return self._snapshots.get(fingerprint_hash)
        
    async def query_by_candidate(self, candidate_id: str) -> List[OptimizationSnapshot]:
        results = []
        for snapshot in self._snapshots.values():
            if snapshot.business_fingerprint.candidate_id == candidate_id:
                results.append(snapshot)
        return results
        
    async def load_latest(self) -> Optional[OptimizationSnapshot]:
        if not self._ordered_ids:
            return None
        latest_key = self._ordered_ids[-1]
        return self._snapshots.get(latest_key)
