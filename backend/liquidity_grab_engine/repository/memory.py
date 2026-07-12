from typing import List, Optional, Dict
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.models.models import LiquidityGrabSnapshot
from backend.liquidity_grab_engine.contracts.repository import ILiquidityGrabRepository

class InMemoryLiquidityGrabRepository(ILiquidityGrabRepository):
    """
    In-memory INSERT-only implementation of the ILiquidityGrabRepository.
    Designed exclusively for testing and validation.
    """
    
    def __init__(self):
        self._snapshots: Dict[str, LiquidityGrabSnapshot] = {}
        
    async def save(self, snapshot: LiquidityGrabSnapshot) -> None:
        if snapshot.snapshot_id in self._snapshots:
            raise ValueError(f"Snapshot with ID {snapshot.snapshot_id} already exists (INSERT-only constraint violated).")
        self._snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabSnapshot]:
        return self._snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._snapshots
        
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabSnapshot]:
        return [s for s in self._snapshots.values() if s.symbol_id == symbol_id]
        
    async def query_by_timeframe(self, timeframe: Timeframe) -> List[LiquidityGrabSnapshot]:
        return [s for s in self._snapshots.values() if s.timeframe == timeframe]
        
    async def query_by_parent_trend_snapshot(self, trend_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        return [s for s in self._snapshots.values() if s.parent_trend_snapshot_version == trend_snapshot_version]
        
    async def query_by_consolidation_snapshot(self, consolidation_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        return [s for s in self._snapshots.values() if s.parent_consolidation_snapshot_version == consolidation_snapshot_version]
        
    async def load_latest(self) -> Optional[LiquidityGrabSnapshot]:
        if not self._snapshots:
            return None
        return max(self._snapshots.values(), key=lambda s: s.created_timestamp)
