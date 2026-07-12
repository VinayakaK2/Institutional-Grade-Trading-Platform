from abc import ABC, abstractmethod
from typing import List, Optional
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport, LiquidityGrabQualityEnum

class ILiquidityGrabQualityRepository(ABC):
    """
    Contract for persisting and querying immutable Liquidity Grab Quality Reports.
    Repository remains INSERT-only.
    """
    
    @abstractmethod
    async def save(self, report: LiquidityGrabQualityReport) -> None:
        pass

    @abstractmethod
    async def load(self, report_id: str) -> Optional[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def exists(self, report_id: str) -> bool:
        pass

    @abstractmethod
    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def query_by_quality(self, quality: LiquidityGrabQualityEnum) -> List[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def query_by_parent_trend_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def query_by_parent_consolidation_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        pass

    @abstractmethod
    async def load_latest(self) -> Optional[LiquidityGrabQualityReport]:
        pass
