import asyncio
from typing import Dict, List, Optional
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.optimization.models import (
    ConsolidationOptimizationSnapshot,
    ConsolidationProcessingResult
)
from backend.consolidation_engine.optimization.contracts import IConsolidationOptimizationRepository

class InMemoryConsolidationOptimizationRepository(IConsolidationOptimizationRepository):
    """
    In-memory implementation for optimization cache and snapshots.
    """
    
    def __init__(self):
        self._snapshots: Dict[str, ConsolidationOptimizationSnapshot] = {}
        self._cached_results: Dict[str, ConsolidationProcessingResult] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, snapshot: ConsolidationOptimizationSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_id in self._snapshots:
                raise ConsolidationRepositoryError(f"Optimization snapshot {snapshot.snapshot_id} already exists.")
            self._snapshots[snapshot.snapshot_id] = snapshot
            
    async def exists(self, fingerprint: str) -> bool:
        # Checking if there's a snapshot with this specific business fingerprint
        return any(s.business_fingerprint == fingerprint for s in self._snapshots.values())
        
    async def load_by_fingerprint(self, fingerprint: str) -> Optional[ConsolidationOptimizationSnapshot]:
        for s in self._snapshots.values():
            if s.business_fingerprint == fingerprint:
                return s
        return None
        
    async def load_latest(self) -> Optional[ConsolidationOptimizationSnapshot]:
        if not self._snapshots:
            return None
        return max(self._snapshots.values(), key=lambda s: s.generated_timestamp)
        
    async def query_by_parent(self, parent_id: str) -> List[ConsolidationOptimizationSnapshot]:
        return [s for s in self._snapshots.values() if s.parent_snapshot_id == parent_id]
        
    async def get_cached_result(self, fingerprint: str) -> Optional[ConsolidationProcessingResult]:
        return self._cached_results.get(fingerprint)
        
    async def save_cached_result(self, result: ConsolidationProcessingResult) -> None:
        async with self._lock:
            self._cached_results[result.fingerprint] = result
