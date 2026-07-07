"""
Watchlist Engine
================

Orchestrates the full watchlist generation lifecycle:

    Caller provides List[WatchlistCandidate]
         │
         │  1. Structural validation via IWatchlistValidator
         ▼
    WatchlistValidator.validate()
         │
         │  2. Build mutable WatchlistExecutionContext
         ▼
    WatchlistExecutionContext (run_id, snapshot_id, candidates)
         │
         │  3. Execute pipeline stages in order
         ▼
    IWatchlistPipeline.execute()
         │
         │  4. Determine next sequential version number
         ▼
    IWatchlistRepository.load_latest_snapshot()
         │
         │  5. Build immutable WatchlistSnapshot (frozen Pydantic model)
         ▼
    WatchlistSnapshot (versioned, pipeline_version stamped)
         │
         │  6. Persist snapshot (INSERT-only — never UPDATE)
         ▼
    IWatchlistRepository.save_snapshot()
         │
         │  7. Return WatchlistResult
         ▼
    WatchlistResult

This engine is an orchestrator ONLY. It must NEVER contain:
  - Candidate selection logic       (belongs in Phase 6.2+)
  - Ranking or scoring              (belongs in Phase 6.3+)
  - Trend or momentum analysis      (belongs in later phases)
  - Business rules of any kind
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import (
    IWatchlistEngine,
    IWatchlistPipeline,
    IWatchlistRepository,
    IWatchlistValidator,
)
from backend.watchlist_engine.models.config import WatchlistSettings
from backend.watchlist_engine.models.models import (
    WatchlistCandidate,
    WatchlistExecutionContext,
    WatchlistResult,
    WatchlistSnapshot,
    WatchlistValidationStatus,
)

logger = get_logger(__name__)


class WatchlistEngine(IWatchlistEngine):
    """
    Orchestrates the full watchlist generation lifecycle.

    Responsibilities:
      - Run structural validation via IWatchlistValidator.
      - Pass the validated candidates through the IWatchlistPipeline.
      - Produce and persist an immutable, versioned WatchlistSnapshot.

    This class must never contain business logic. All future phases
    (candidate filtering, scoring, ranking) are implemented as IWatchlistStage
    instances registered into the pipeline from outside this engine.

    The engine is STATELESS. It retains no candidate data between runs.
    The same engine instance can safely serve multiple concurrent runs.
    """

    def __init__(
        self,
        settings: WatchlistSettings,
        pipeline: IWatchlistPipeline,
        repository: IWatchlistRepository,
        validator: IWatchlistValidator,
    ) -> None:
        self._settings = settings
        self._pipeline = pipeline
        self._repository = repository
        self._validator = validator

        # Pipeline version is read from settings and stamped on every snapshot.
        # Increment the version in WatchlistSnapshotSettings when pipeline logic changes.
        self._pipeline_version = settings.snapshot.pipeline_version

    async def generate_watchlist(
        self,
        run_id: str,
        candidates: List[WatchlistCandidate],
        source_universe_snapshot_id: Optional[str] = None,
        source_universe_version: Optional[int] = None,
        config_hash: str = "unknown",
        candidate_selection_version: Optional[str] = None,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> WatchlistResult:
        """
        Execute a full watchlist generation run and return an immutable snapshot.

        Steps:
          1. Run structural validation (duplicates, nulls, empty checks).
          2. Build an execution context and pass it through the pipeline.
          3. Increment the version counter from the latest persisted snapshot.
          4. Build an immutable WatchlistSnapshot (frozen Pydantic model).
          5. Persist the snapshot via INSERT-only repository write.
          6. Return a WatchlistResult wrapping the snapshot.

        Args:
            run_id: Unique identifier for this run — used for tracing and metadata.
            candidates: Pre-processed WatchlistCandidate symbols to include.

        Returns:
            WatchlistResult containing the newly created WatchlistSnapshot.

        Raises:
            WatchlistValidationError: If structural validation of candidates fails.
            WatchlistPipelineError: If any pipeline stage raises an unhandled exception.
            WatchlistRepositoryError: If snapshot persistence fails.
        """
        logger.info(
            f"Starting Watchlist Generation [Run: {run_id}] "
            f"| Candidates: {len(candidates)} "
            f"| Pipeline Version: {self._pipeline_version}"
        )

        snapshot_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        # ── Step 1: Structural validation ─────────────────────────────────────
        # Validates for duplicates, null entries, and empty candidate lists.
        # If validation fails, we abort immediately — no snapshot is created.
        try:
            self._validator.validate(candidates)
            validation_status = WatchlistValidationStatus.PASSED
            logger.info(f"Structural validation passed for {len(candidates)} candidates.")
        except Exception as exc:
            logger.error(f"Watchlist validation failed for run {run_id}: {str(exc)}")
            validation_status = WatchlistValidationStatus.FAILED
            raise

        # ── Step 2: Build execution context ───────────────────────────────────
        # The context is mutable during the pipeline so stages can accumulate results.
        metadata = {"source": "WatchlistEngine", "pipeline_version": self._pipeline_version}
        if metadata_overrides:
            metadata.update(metadata_overrides)

        context = WatchlistExecutionContext(
            run_id=run_id,
            snapshot_id=snapshot_id,
            started_at=started_at,
            candidates=list(candidates),  # Shallow copy — engine does not mutate caller's list.
            shared_state={},
            metadata=metadata,
            stage_results=[],
        )

        # ── Step 3: Execute pipeline stages ───────────────────────────────────
        initial_candidate_count = len(context.candidates)
        context = await self._pipeline.execute(context)
        final_candidate_count = len(context.candidates)

        # Aggregate pipeline execution statistics.
        context.metadata["pipeline_statistics"] = {
            "initial_candidate_count": initial_candidate_count,
            "final_candidate_count": final_candidate_count,
            "stages_executed": len(context.stage_results),
        }

        # ── Step 4: Determine the next sequential version number ─────────────
        # Always persist a NEW snapshot — never overwrite an existing one.
        latest = await self._repository.load_latest_snapshot()
        version = (latest.version + 1) if latest else 1

        # ── Step 5: Build immutable snapshot ──────────────────────────────────
        # WatchlistSnapshot is a frozen Pydantic model. Once created, it is final.
        snapshot = WatchlistSnapshot(
            snapshot_id=context.snapshot_id,
            version=version,
            created_at=datetime.now(timezone.utc),
            symbol_count=len(context.candidates),
            candidates=context.candidates,
            metadata={
                "run_id": context.run_id,
                "execution_time_ms": (
                    datetime.now(timezone.utc) - context.started_at
                ).total_seconds() * 1000,
                "stage_results": [res.model_dump(mode="json") for res in context.stage_results],
                **context.metadata,
            },
            pipeline_version=self._pipeline_version,
            config_hash=config_hash,
            validation_status=validation_status,
            source_universe_snapshot_id=source_universe_snapshot_id,
            source_universe_version=source_universe_version,
            candidate_selection_version=candidate_selection_version,
        )

        # ── Step 6: Persist snapshot (INSERT-only) ───────────────────────────
        await self._repository.save_snapshot(snapshot)
        logger.info(
            f"Successfully generated and saved WatchlistSnapshot "
            f"{snapshot_id} (Version {version}, Pipeline {self._pipeline_version})"
        )

        # ── Step 7: Return result ─────────────────────────────────────────────
        return WatchlistResult(snapshot=snapshot)
