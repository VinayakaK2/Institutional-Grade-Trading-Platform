from abc import ABC, abstractmethod
from typing import List, Optional
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate

class ILiquidityGrabDetectionRepository(ABC):
    """
    Contract for persisting and querying immutable Liquidity Grab Candidates.
    This repository is strictly insert-only and decoupled from Foundation Snapshots.
    """
    
    @abstractmethod
    async def save(self, candidate: LiquidityGrabCandidate) -> None:
        pass

    @abstractmethod
    async def load(self, candidate_id: str) -> Optional[LiquidityGrabCandidate]:
        pass

    @abstractmethod
    async def exists(self, candidate_id: str) -> bool:
        pass

    @abstractmethod
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabCandidate]:
        pass

    @abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[LiquidityGrabCandidate]:
        pass

    @abstractmethod
    async def query_by_parent_trend_snapshot(self, snapshot_version: int) -> List[LiquidityGrabCandidate]:
        pass

    @abstractmethod
    async def query_by_parent_consolidation_snapshot(self, snapshot_version: int) -> List[LiquidityGrabCandidate]:
        pass
        
    @abstractmethod
    async def query_by_dataset_version(self, dataset_version: int) -> List[LiquidityGrabCandidate]:
        """
        Query candidates by canonical dataset version for replay, debugging,
        and historical verification.
        """
        pass

    @abstractmethod
    async def load_latest(self) -> Optional[LiquidityGrabCandidate]:
        pass
