from typing import List, Optional
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.models.models import LiquidityGrabSnapshot
from backend.liquidity_grab_engine.contracts.repository import ILiquidityGrabRepository

class PostgreSQLLiquidityGrabRepository(ILiquidityGrabRepository):
    """
    PostgreSQL implementation of the ILiquidityGrabRepository.
    Currently unimplemented for Phase 9.1 to avoid fake persistence logic.
    Raises NotImplementedError on all operations.
    """
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        
    async def save(self, snapshot: LiquidityGrabSnapshot) -> None:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def exists(self, snapshot_id: str) -> bool:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def query_by_timeframe(self, timeframe: Timeframe) -> List[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def query_by_parent_trend_snapshot(self, trend_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def query_by_consolidation_snapshot(self, consolidation_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
        
    async def load_latest(self) -> Optional[LiquidityGrabSnapshot]:
        raise NotImplementedError("PostgreSQL implementation deferred.")
