"""
In-Memory Quality Repository
============================

In-memory implementation of the ITrendQualityRepository for testing and isolation.
"""

from typing import Dict, Optional
from backend.trend_engine.quality.contracts.contracts import ITrendQualityRepository
from backend.trend_engine.quality.models.models import TrendQualitySnapshot
from backend.trend_engine.quality.exceptions import DuplicateQualityEvaluationError


class InMemoryTrendQualityRepository(ITrendQualityRepository):
    """
    Thread-safe (simulated via async/dictionary) memory repository for Trend Quality Snapshots.
    """
    
    def __init__(self) -> None:
        # Maps quality_snapshot_id -> TrendQualitySnapshot
        self._snapshots: Dict[str, TrendQualitySnapshot] = {}
        # Maps source_trend_snapshot_id -> TrendQualitySnapshot
        self._parent_index: Dict[str, TrendQualitySnapshot] = {}

    async def save_quality_snapshot(self, snapshot: TrendQualitySnapshot) -> None:
        """
        Saves a new snapshot. Raises DuplicateQualityEvaluationError if ID already exists.
        """
        if snapshot.quality_snapshot_id in self._snapshots:
            raise DuplicateQualityEvaluationError(f"TrendQualitySnapshot with ID {snapshot.quality_snapshot_id} already exists.")
            
        self._snapshots[snapshot.quality_snapshot_id] = snapshot
        
        # In a real database this might be a one-to-many relationship, but for Phase 7.3 we keep the latest.
        self._parent_index[snapshot.source_trend_snapshot_id] = snapshot

    async def get_quality_snapshot(self, snapshot_id: str) -> Optional[TrendQualitySnapshot]:
        return self._snapshots.get(snapshot_id)

    async def get_latest_quality_for_trend(self, trend_snapshot_id: str) -> Optional[TrendQualitySnapshot]:
        return self._parent_index.get(trend_snapshot_id)
