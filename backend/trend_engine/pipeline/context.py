"""
Trend Engine Pipeline Execution Context
=======================================

Mutable state object passed through the Trend Pipeline.

EXECUTION CONTEXT IS RUNTIME INFRASTRUCTURE, NOT A DOMAIN MODEL.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

from backend.trend_engine.models.models import TrendSymbol, TrendStageResult


class TrendExecutionContext(BaseModel):
    """
    Mutable execution context that is passed through all pipeline stages.

    Stages may:
      - Append to `stage_results` after they complete.
      - Write intermediate data into `shared_state` for downstream stages.
      - Append structured execution metadata into `metadata`.
      - Read from `symbols` but must NOT mutate TrendSymbol identity.

    The context is NOT frozen because pipeline stages must accumulate results.
    After the pipeline completes, an immutable TrendSnapshot is derived from it.
    """
    run_id: str
    
    # Lineage IDs required for tracking
    source_watchlist_snapshot_id: str
    source_watchlist_version: int

    source_indicator_snapshot_id: str
    source_indicator_snapshot_version: int

    source_structure_snapshot_id: str
    source_structure_snapshot_version: int

    started_at: datetime
    symbols: List[TrendSymbol]
    
    # Configuration and Pipeline Versioning
    configuration_hash: str
    pipeline_version: str
    schema_version: str

    shared_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stage_results: List[TrendStageResult] = Field(default_factory=list)

    @property
    def is_cancelled(self) -> bool:
        """
        Check if execution has been cancelled.
        (Placeholder for real cancellation support)
        """
        return self.metadata.get("cancelled", False)

    def cancel(self, reason: str) -> None:
        """
        Mark the context as cancelled.
        """
        self.metadata["cancelled"] = True
        self.metadata["cancellation_reason"] = reason
