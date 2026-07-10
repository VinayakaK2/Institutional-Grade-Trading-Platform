"""
Trend Engine Core Orchestrator
==============================

Coordinates Validation, Pipeline execution, Snapshot construction, and Persistence.
Does NOT perform trend detection or build snapshots itself.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from backend.trend_engine.contracts.contracts import (
    ITrendEngine,
    ITrendPipeline,
    ITrendRepository,
    ITrendValidator,
    ITrendSnapshotBuilder,
)
from backend.trend_engine.models.models import TrendSymbol, TrendSnapshot
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.config.config import TrendSettings

logger = logging.getLogger(__name__)


class TrendEngine(ITrendEngine):
    """
    Core orchestrator for the Trend Engine.
    
    Responsibilities:
      - Validates inputs
      - Initializes the ExecutionContext
      - Executes the Pipeline
      - Delegates Snapshot Construction
      - Persists the Snapshot
      
    Remains completely stateless, thread-safe, and asynchronous.
    """

    def __init__(
        self,
        pipeline: ITrendPipeline,
        repository: ITrendRepository,
        validator: ITrendValidator,
        snapshot_builder: ITrendSnapshotBuilder,
        settings: TrendSettings,
    ):
        self._pipeline = pipeline
        self._repository = repository
        self._validator = validator
        self._snapshot_builder = snapshot_builder
        self._settings = settings

    async def generate_trend_snapshot(
        self,
        symbols: List[TrendSymbol],
        source_watchlist_snapshot_id: str,
        source_watchlist_version: int,
        source_indicator_snapshot_id: str,
        source_indicator_snapshot_version: int,
        source_structure_snapshot_id: str,
        source_structure_snapshot_version: int,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> TrendSnapshot:
        """
        Executes the full pipeline and returns a persisted, immutable TrendSnapshot.
        """
        logger.info(
            f"Starting Trend Engine execution. "
            f"Input symbols: {len(symbols)}, "
            f"Source Watchlist: {source_watchlist_snapshot_id} (v{source_watchlist_version})"
        )
        
        # 1. Structural Validation
        self._validator.validate_input(symbols)
        
        # 2. Determine next snapshot version
        latest_snapshot = await self._repository.load_latest_snapshot()
        next_version = (latest_snapshot.snapshot_version + 1) if latest_snapshot else 1

        # 3. Context Initialization
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        
        config_hash = self._settings.generate_hash()
        
        context = TrendExecutionContext(
            run_id=run_id,
            source_watchlist_snapshot_id=source_watchlist_snapshot_id,
            source_watchlist_version=source_watchlist_version,
            source_indicator_snapshot_id=source_indicator_snapshot_id,
            source_indicator_snapshot_version=source_indicator_snapshot_version,
            source_structure_snapshot_id=source_structure_snapshot_id,
            source_structure_snapshot_version=source_structure_snapshot_version,
            started_at=started_at,
            symbols=symbols,
            configuration_hash=config_hash,
            pipeline_version="1.0.0",
            schema_version=self._settings.schema_version,
            metadata=metadata_overrides or {}
        )
        
        # 4. Pipeline Execution
        context = await self._pipeline.execute(context)
        
        if context.is_cancelled:
            logger.warning(f"Trend execution cancelled: {context.metadata.get('cancellation_reason')}")
            # If cancelled, we don't build or persist a snapshot.
            # In a real system, we might raise an error or return a partial failure.
            raise RuntimeError("Pipeline was cancelled.")

        # 5. Snapshot Construction
        snapshot = self._snapshot_builder.build_snapshot(context, next_version)
        
        # 6. Snapshot Validation (Ensure immutability and rules before persistence)
        self._validator.validate_snapshot(snapshot, latest_snapshot)

        # 7. Persistence
        await self._repository.save_snapshot(snapshot)
        
        logger.info(
            f"Trend Engine execution complete. "
            f"Generated Snapshot: {snapshot.snapshot_id} (v{snapshot.snapshot_version})"
        )
        
        return snapshot
