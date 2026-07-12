from typing import Optional, List
from backend.liquidity_grab_engine.lifecycle.contracts.repository import ILiquidityGrabLifecycleRepository
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot, LiquidityGrabLifecycleState

class PostgreSQLLifecycleRepository(ILiquidityGrabLifecycleRepository):
    async def save(self, snapshot: LiquidityGrabLifecycleSnapshot) -> None:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def exists(self, snapshot_id: str) -> bool:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def query_by_state(self, state: LiquidityGrabLifecycleState) -> List[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")
        
    async def query_by_quality_report(self, report_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")

    async def load_latest(self, candidate_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        raise NotImplementedError("PostgreSQLLifecycleRepository is not implemented in Phase 9.4.")
