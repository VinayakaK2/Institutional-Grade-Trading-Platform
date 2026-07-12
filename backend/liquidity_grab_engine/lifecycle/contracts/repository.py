from abc import ABC, abstractmethod
from typing import Optional, List
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot, LiquidityGrabLifecycleState

class ILiquidityGrabLifecycleRepository(ABC):
    @abstractmethod
    async def save(self, snapshot: LiquidityGrabLifecycleSnapshot) -> None:
        pass

    @abstractmethod
    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        pass

    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass

    @abstractmethod
    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        pass

    @abstractmethod
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        pass

    @abstractmethod
    async def query_by_state(self, state: LiquidityGrabLifecycleState) -> List[LiquidityGrabLifecycleSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_quality_report(self, report_id: str) -> List[LiquidityGrabLifecycleSnapshot]:
        pass

    @abstractmethod
    async def load_latest(self, candidate_id: str) -> Optional[LiquidityGrabLifecycleSnapshot]:
        pass
