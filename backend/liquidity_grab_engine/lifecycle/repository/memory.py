from typing import Optional, List, Dict
from backend.liquidity_grab_engine.lifecycle.contracts.repository import ILiquidityGrabLifecycleRepository
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot, LiquidityGrabLifecycleState

class InMemoryLifecycleRepository(ILiquidityGrabLifecycleRepository):
    def __init__(self) -> None:
        self._store: Dict[str, LiquidityGrabLifecycleSnapshot] = {}

    async def save(self, snapshot: LiquidityGrabLifecycleSnapshot) -> None:
        self._store[snapshot.snapshot_id] = snapshot

    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        return self._store.get(snapshot_id)

    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._store

    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        return [s for s in self._store.values() if s.candidate_id == candidate_id]

    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        return [s for s in self._store.values() if s.symbol_id == symbol_id]

    async def query_by_state(self, state: LiquidityGrabLifecycleState) -> List[LiquidityGrabLifecycleSnapshot]:
        return [s for s in self._store.values() if s.summary.state == state]
        
    async def query_by_quality_report(self, report_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        return [s for s in self._store.values() if s.metadata.get("quality_report_id") == report_id]

    async def load_latest(self, candidate_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        candidate_snapshots = await self.query_by_candidate(candidate_id)
        if not candidate_snapshots:
            return None
        return sorted(candidate_snapshots, key=lambda s: s.metadata.get("generated_at", ""), reverse=True)[0]
