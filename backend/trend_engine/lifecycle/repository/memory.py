from typing import Dict, Optional
from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleRepository
from backend.trend_engine.lifecycle.models.models import TrendLifecycleSnapshot

class InMemoryTrendLifecycleRepository(ITrendLifecycleRepository):
    """
    Thread-safe (simulated via async/dictionary) memory repository for Trend Lifecycle Snapshots.
    """
    
    def __init__(self) -> None:
        # Maps lifecycle_snapshot_id -> TrendLifecycleSnapshot
        self._snapshots: Dict[str, TrendLifecycleSnapshot] = {}
        # Maps parent_trend_snapshot_id -> latest TrendLifecycleSnapshot
        self._latest_by_parent: Dict[str, TrendLifecycleSnapshot] = {}
        
    async def save_lifecycle_snapshot(self, snapshot: TrendLifecycleSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot
        
        # In a real DB this would be handled by ordering/timestamps.
        # Since snapshot IDs are generated sequentially (e.g. ULIDs) or by versions, 
        # overwriting the latest by parent is a simplified representation.
        # For memory tests we assume saving sequentially means it's the latest.
        self._latest_by_parent[snapshot.parent_trend_snapshot_id] = snapshot
        
    async def get_lifecycle_snapshot(self, snapshot_id: str) -> Optional[TrendLifecycleSnapshot]:
        return self._snapshots.get(snapshot_id)
        
    async def get_latest_for_parent_snapshot(self, parent_trend_snapshot_id: str) -> Optional[TrendLifecycleSnapshot]:
        return self._latest_by_parent.get(parent_trend_snapshot_id)

    async def exists_for_parent_snapshot(self, parent_trend_snapshot_id: str) -> bool:
        return parent_trend_snapshot_id in self._latest_by_parent
