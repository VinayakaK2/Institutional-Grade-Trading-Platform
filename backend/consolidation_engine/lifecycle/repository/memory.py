import asyncio
from typing import Dict, List, Optional
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.lifecycle.models import ConsolidationLifecycleSnapshot, ConsolidationLifecycleState
from backend.consolidation_engine.lifecycle.contracts import IConsolidationLifecycleRepository

class InMemoryConsolidationLifecycleRepository(IConsolidationLifecycleRepository):
    """
    In-memory implementation of IConsolidationLifecycleRepository.
    """
    
    def __init__(self):
        self._snapshots: Dict[str, ConsolidationLifecycleSnapshot] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, snapshot: ConsolidationLifecycleSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_id in self._snapshots:
                raise ConsolidationRepositoryError(f"Lifecycle snapshot {snapshot.snapshot_id} already exists.")
            self._snapshots[snapshot.snapshot_id] = snapshot
            
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._snapshots
        
    async def load_by_snapshot_id(self, snapshot_id: str) -> Optional[ConsolidationLifecycleSnapshot]:
        return self._snapshots.get(snapshot_id)
        
    async def load_latest(self, candidate_id: str) -> Optional[ConsolidationLifecycleSnapshot]:
        # Return the most recently generated snapshot for this candidate
        candidate_snapshots = [s for s in self._snapshots.values() if s.candidate_id == candidate_id]
        if not candidate_snapshots:
            return None
        return max(candidate_snapshots, key=lambda s: s.generated_timestamp)
        
    async def query_by_symbol(self, symbol: str) -> List[ConsolidationLifecycleSnapshot]:
        return [s for s in self._snapshots.values() if s.symbol == symbol]
        
    async def query_by_timeframe(self, timeframe: str) -> List[ConsolidationLifecycleSnapshot]:
        return [s for s in self._snapshots.values() if s.timeframe == timeframe]
        
    async def query_by_state(self, state: ConsolidationLifecycleState) -> List[ConsolidationLifecycleSnapshot]:
        return [s for s in self._snapshots.values() if s.lifecycle_state == state]
