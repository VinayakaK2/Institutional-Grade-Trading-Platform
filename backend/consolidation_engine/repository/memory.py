import asyncio
from typing import Optional, Dict, List
from backend.consolidation_engine.models.models import ConsolidationSnapshot, ConsolidationCandidate
from backend.consolidation_engine.contracts.contracts import IConsolidationRepository
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError

class InMemoryConsolidationRepository(IConsolidationRepository):
    """
    In-memory INSERT-only repository for testing and certification.
    """
    
    def __init__(self):
        self._snapshots: Dict[int, ConsolidationSnapshot] = {}
        self._lock = asyncio.Lock()
        
    async def save_snapshot(self, snapshot: ConsolidationSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_version in self._snapshots:
                raise ConsolidationRepositoryError(f"Snapshot version {snapshot.snapshot_version} already exists. UPDATE is not allowed.")
            self._snapshots[snapshot.snapshot_version] = snapshot
            
    async def load_snapshot_by_version(self, snapshot_version: int) -> Optional[ConsolidationSnapshot]:
        return self._snapshots.get(snapshot_version)
        
    async def load_latest_snapshot(self) -> Optional[ConsolidationSnapshot]:
        if not self._snapshots:
            return None
        max_version = max(self._snapshots.keys())
        return self._snapshots[max_version]
        
    async def load_historical_snapshots(self, limit: int = 10) -> List[ConsolidationSnapshot]:
        sorted_versions = sorted(self._snapshots.keys(), reverse=True)
        return [self._snapshots[v] for v in sorted_versions[:limit]]

    async def exists(self, snapshot_version: int) -> bool:
        return snapshot_version in self._snapshots
        
    async def query_by_parent_trend_snapshot(self, parent_version: int) -> List[ConsolidationSnapshot]:
        return [s for s in self._snapshots.values() if s.parent_trend_snapshot_version == parent_version]
        
    async def query_by_symbol(self, symbol: str) -> List["ConsolidationCandidate"]:
        candidates = []
        for s in self._snapshots.values():
            candidates.extend([c for c in s.candidates if c.symbol == symbol])
        return candidates
        
    async def query_by_timeframe(self, timeframe: str) -> List["ConsolidationCandidate"]:
        candidates = []
        for s in self._snapshots.values():
            candidates.extend([c for c in s.candidates if c.timeframe == timeframe])
        return candidates
