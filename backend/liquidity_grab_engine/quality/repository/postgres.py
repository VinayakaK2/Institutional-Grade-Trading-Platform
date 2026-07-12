from typing import List, Optional
from backend.liquidity_grab_engine.quality.contracts.repository import ILiquidityGrabQualityRepository
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport, LiquidityGrabQualityEnum

class PostgreSQLQualityRepository(ILiquidityGrabQualityRepository):
    """
    PostgreSQL adapter for the Quality Repository.
    Implementation deferred.
    """
    async def save(self, report: LiquidityGrabQualityReport) -> None:
        raise NotImplementedError

    async def load(self, report_id: str) -> Optional[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def exists(self, report_id: str) -> bool:
        raise NotImplementedError

    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def query_by_quality(self, quality: LiquidityGrabQualityEnum) -> List[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def query_by_parent_trend_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def query_by_parent_consolidation_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        raise NotImplementedError

    async def load_latest(self) -> Optional[LiquidityGrabQualityReport]:
        raise NotImplementedError
