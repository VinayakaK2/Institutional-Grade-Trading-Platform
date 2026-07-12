import logging
from typing import List, Optional
from backend.liquidity_grab_engine.quality.contracts.repository import ILiquidityGrabQualityRepository
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport, LiquidityGrabQualityEnum

logger = logging.getLogger(__name__)

class InMemoryQualityRepository(ILiquidityGrabQualityRepository):
    """
    In-memory adapter for the Quality Repository.
    """
    def __init__(self):
        self._reports: List[LiquidityGrabQualityReport] = []

    async def save(self, report: LiquidityGrabQualityReport) -> None:
        self._reports.append(report)
        logger.debug(f"Saved quality report {report.report_id}")

    async def load(self, report_id: str) -> Optional[LiquidityGrabQualityReport]:
        return next((r for r in self._reports if r.report_id == report_id), None)

    async def exists(self, report_id: str) -> bool:
        return any(r.report_id == report_id for r in self._reports)

    async def query_by_candidate(self, candidate_id: str) -> List[LiquidityGrabQualityReport]:
        return [r for r in self._reports if r.candidate_id == candidate_id]

    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabQualityReport]:
        return [r for r in self._reports if r.symbol_id == symbol_id]

    async def query_by_quality(self, quality: LiquidityGrabQualityEnum) -> List[LiquidityGrabQualityReport]:
        return [r for r in self._reports if r.classification.quality == quality]

    async def query_by_parent_trend_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        return [r for r in self._reports if r.parent_trend_snapshot_version == snapshot_version]

    async def query_by_parent_consolidation_snapshot(self, snapshot_version: int) -> List[LiquidityGrabQualityReport]:
        return [r for r in self._reports if r.parent_consolidation_snapshot_version == snapshot_version]

    async def load_latest(self) -> Optional[LiquidityGrabQualityReport]:
        if not self._reports:
            return None
        return max(self._reports, key=lambda r: r.metadata.created_timestamp)
