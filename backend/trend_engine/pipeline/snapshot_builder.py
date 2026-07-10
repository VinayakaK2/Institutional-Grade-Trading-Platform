"""
Trend Engine Snapshot Builder
=============================

Responsible for cleanly constructing the immutable TrendSnapshot.
The Engine delegates to this builder after the pipeline completes.
"""
import uuid
from datetime import datetime, timezone

from backend.trend_engine.contracts.contracts import ITrendSnapshotBuilder
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.models.models import TrendSnapshot


class SnapshotBuilder(ITrendSnapshotBuilder):
    """
    Constructs the final TrendSnapshot from the execution context.
    """

    def build_snapshot(self, context: TrendExecutionContext, next_version: int) -> TrendSnapshot:
        """
        Builds the immutable TrendSnapshot object.
        
        Args:
            context: The finished execution context.
            next_version: The strict monotonically incremented version number.
        """
        now = datetime.now(timezone.utc)
        
        # Calculate execution duration
        duration_ms = (now - context.started_at).total_seconds() * 1000

        # Construct basic execution metadata
        execution_metadata = {
            "run_id": context.run_id,
            "duration_ms": duration_ms,
            "symbol_count": len(context.symbols),
            **context.metadata
        }

        # Construct audit metadata from stage results
        audit_metadata = {
            "stage_results": [r.model_dump() for r in context.stage_results]
        }
        
        snapshot = TrendSnapshot(
            snapshot_id=str(uuid.uuid4()),
            snapshot_version=next_version,
            source_watchlist_snapshot_id=context.source_watchlist_snapshot_id,
            source_watchlist_version=context.source_watchlist_version,
            source_indicator_snapshot_id=context.source_indicator_snapshot_id,
            source_indicator_snapshot_version=context.source_indicator_snapshot_version,
            source_structure_snapshot_id=context.source_structure_snapshot_id,
            source_structure_snapshot_version=context.source_structure_snapshot_version,
            created_at=now,
            symbols=list(context.symbols),  # Shallow copy the list to prevent external list mutation
            pipeline_version=context.pipeline_version,
            configuration_hash=context.configuration_hash,
            schema_version=context.schema_version,
            execution_metadata=execution_metadata,
            audit_metadata=audit_metadata
        )
        
        return snapshot
