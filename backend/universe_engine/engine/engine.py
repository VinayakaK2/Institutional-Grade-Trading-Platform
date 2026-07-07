"""
Universe Engine
===============

Coordinates the full execution lifecycle for universe generation:

    IUniverseProvider
         │
         │  fetch_universe() → List[SymbolReference]
         ▼
    UniverseValidator
         │
         │  validate_symbols() → raises UniverseValidationError on failure
         ▼
    UniverseExecutionContext  (created, then mutated through the pipeline)
         │
         │  passed through each registered IUniverseStage in order
         ▼
    IUniversePipeline.execute()
         │
         │  produces StageResult per stage
         ▼
    UniverseSnapshot          (immutable, versioned, stamped with pipeline_version)
         │
         │  saved via IUniverseRepository (INSERT-only — never UPDATE)
         ▼
    UniverseResult            (returned to the caller)

This engine is an orchestrator ONLY. It must NEVER contain:
  - Filtering logic           (belongs in Phase 5.2+)
  - Scoring or ranking        (belongs in Phase 5.3+)
  - Trend or momentum logic   (belongs in the Market Analysis module)
  - Watchlist management      (belongs in Phase 5.5+)
"""
from datetime import datetime, timezone
import uuid

from backend.universe_engine.contracts.engine import IUniverseEngine
from backend.universe_engine.contracts.provider import IUniverseProvider
from backend.universe_engine.contracts.pipeline import IUniversePipeline
from backend.universe_engine.contracts.repository import IUniverseRepository
from backend.universe_engine.contracts.validator import IUniverseValidator
from backend.universe_engine.models.universe import (
    UniverseResult,
    UniverseSnapshot,
    UniverseExecutionContext,
    ValidationStatus,
)
from backend.universe_engine.models.config import UniverseSettings
from backend.core.logger import get_logger

logger = get_logger(__name__)


class UniverseEngine(IUniverseEngine):
    """
    Orchestrates the full universe generation lifecycle.

    Responsibilities:
      - Fetch the raw symbol list from an IUniverseProvider.
      - Run structural validation via IUniverseValidator.
      - Pass the validated symbols through the IUniversePipeline.
      - Produce and persist an immutable, versioned UniverseSnapshot.

    This class must never contain business logic. All future phases
    (filtering, scoring, ranking) are implemented as IUniverseStage
    instances registered into the pipeline from outside this engine.
    """

    def __init__(
        self,
        settings: UniverseSettings,
        provider: IUniverseProvider,
        pipeline: IUniversePipeline,
        repository: IUniverseRepository,
        validator: IUniverseValidator,
    ):
        self._settings = settings
        self._provider = provider
        self._pipeline = pipeline
        self._repository = repository
        self._validator = validator

        # Read pipeline_version from settings so it is stamped correctly on
        # every snapshot. When the pipeline evolves, increment the version in
        # UniverseSettings — not here. See models/config.py for versioning rules.
        self._pipeline_version = settings.pipeline_version

    async def generate_universe(self, run_id: str) -> UniverseResult:
        """
        Execute a full universe generation run and return an immutable snapshot.

        Steps:
          1. Fetch raw symbols from provider.
          2. Run structural validation (duplicates, nulls, empty checks).
          3. Build an execution context and pass it through the pipeline.
          4. Increment the version counter from the latest persisted snapshot.
          5. Build an immutable UniverseSnapshot (frozen Pydantic model).
          6. Persist the snapshot via INSERT-only repository write.
          7. Return a UniverseResult wrapping the snapshot.

        Args:
            run_id: Unique identifier for this run — used for tracing and metadata.

        Returns:
            UniverseResult containing the newly created UniverseSnapshot.

        Raises:
            UniverseValidationError: If structural validation of symbols fails.
            UniversePipelineError: If any pipeline stage raises an unhandled exception.
        """
        logger.info(
            f"Starting Universe Generation [Run: {run_id}] "
            f"using Provider: {self._provider.provider_name} "
            f"| Pipeline Version: {self._pipeline_version}"
        )

        snapshot_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        # ── Step 1: Fetch raw instruments from the configured provider ──────────
        raw_instruments = await self._provider.fetch_universe()
        logger.info(f"Fetched {len(raw_instruments)} instruments from {self._provider.provider_name}")

        # ── Step 2: Structural validation ────────────────────────────────────
        # Validates for duplicates, null entries, and empty universes.
        # If validation fails, we abort immediately — no snapshot is created.
        try:
            self._validator.validate_symbols(raw_instruments)
            validation_status = ValidationStatus.PASSED
        except Exception as e:
            logger.error(f"Validation failed for run {run_id}: {str(e)}")
            validation_status = ValidationStatus.FAILED
            raise

        # ── Step 3: Build execution context ──────────────────────────────────
        # The context is mutable during the pipeline so stages can append results.
        context = UniverseExecutionContext(
            run_id=run_id,
            snapshot_id=snapshot_id,
            provider_name=self._provider.provider_name,
            started_at=started_at,
            instruments=raw_instruments,
            shared_state={},
            metadata={"source": "UniverseEngine", "pipeline_version": self._pipeline_version},
            stage_results=[],
        )

        # ── Step 4: Execute pipeline stages ───────────────────────────────────
        # Each registered IUniverseStage runs in order. The pipeline halts on
        # the first FAILED stage result. Unhandled exceptions are wrapped into
        # UniversePipelineError before being raised.
        initial_instrument_count = len(context.instruments)
        context = await self._pipeline.execute(context)
        final_instrument_count = len(context.instruments)

        # ── Step 4b: Aggregate Filtering Statistics ───────────────────────────
        filtering_statistics = {
            "initial_instrument_count": initial_instrument_count,
            "final_instrument_count": final_instrument_count,
        }
        for result in context.stage_results:
            if "rejected_count" in result.metadata:
                stage_key = result.stage_name.replace("Stage", "").replace("Filter", "_rejections").lower()
                filtering_statistics[stage_key] = result.metadata["rejected_count"]
                
        context.metadata["filtering_statistics"] = filtering_statistics

        # ── Step 5: Determine the next sequential version number ─────────────
        # We always persist a NEW snapshot — never overwrite an existing one.
        latest = await self._repository.load_latest_snapshot()
        version = (latest.version + 1) if latest else 1

        # ── Step 6: Build immutable snapshot ─────────────────────────────────
        # UniverseSnapshot is a frozen Pydantic model. It must never be mutated
        # after creation. All future pipeline runs create a new snapshot instead.
        snapshot = UniverseSnapshot(
            snapshot_id=context.snapshot_id,
            version=version,
            provider=context.provider_name,
            created_at=datetime.now(timezone.utc),
            symbol_count=len(context.instruments),
            instruments=context.instruments,
            metadata={
                "run_id": context.run_id,
                "execution_time_ms": (
                    datetime.now(timezone.utc) - context.started_at
                ).total_seconds() * 1000,
                "stage_results": [res.model_dump(mode="json") for res in context.stage_results],
                **context.metadata,
            },
            pipeline_version=self._pipeline_version,
            validation_status=validation_status,
        )

        # ── Step 7: Persist snapshot (INSERT-only) ───────────────────────────
        await self._repository.save_snapshot(snapshot)
        logger.info(
            f"Successfully generated and saved Universe Snapshot "
            f"{snapshot_id} (Version {version}, Pipeline {self._pipeline_version})"
        )

        # ── Step 8: Return result ─────────────────────────────────────────────
        return UniverseResult(snapshot=snapshot)
