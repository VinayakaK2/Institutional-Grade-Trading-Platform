"""
Watchlist Execution Pipeline
=============================

Reusable, ordered execution pipeline for watchlist pipeline stages.

Responsibilities:
  - Register stages up to a configured maximum.
  - Execute stages in registration order.
  - Propagate the mutable WatchlistExecutionContext through every stage.
  - Record an immutable WatchlistStageResult per stage.
  - Halt immediately on the first FAILED stage result (fail-fast policy).
  - Wrap unhandled stage exceptions in WatchlistPipelineError before re-raising.

This pipeline contains NO selection logic, NO business rules, and NO filtering.
It is a pure orchestrator of registered IWatchlistStage instances.
"""
import time
from typing import List

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistPipeline, IWatchlistStage
from backend.watchlist_engine.models.models import (
    WatchlistExecutionContext,
    WatchlistStageResult,
    WatchlistStageStatus,
)
from backend.watchlist_engine.models.config import WatchlistPipelineSettings
from backend.watchlist_engine.models.exceptions import WatchlistPipelineError

logger = get_logger(__name__)


class WatchlistExecutionPipeline(IWatchlistPipeline):
    """
    Concrete implementation of IWatchlistPipeline.

    Executes registered IWatchlistStage instances sequentially.
    Halts on first FAILED stage. Wraps unexpected exceptions in
    WatchlistPipelineError to maintain a consistent error contract.
    """

    def __init__(self, settings: WatchlistPipelineSettings) -> None:
        self._stages: List[IWatchlistStage] = []
        self._settings = settings

    def register_stage(self, stage: IWatchlistStage) -> None:
        """
        Registers a stage into the pipeline.

        Raises:
            WatchlistPipelineError: If maximum stage count would be exceeded.
        """
        if len(self._stages) >= self._settings.max_stages:
            raise WatchlistPipelineError(
                f"Maximum pipeline stages ({self._settings.max_stages}) exceeded. "
                "Cannot register additional stages.",
                details={"stage_name": stage.name, "current_count": len(self._stages)},
            )
        self._stages.append(stage)
        logger.debug(f"Registered watchlist pipeline stage: {stage.name}")

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistExecutionContext:
        """
        Executes all registered stages in order against the context.

        Behaviour:
          - If a stage returns WatchlistStageStatus.FAILED, the pipeline halts.
          - If a stage raises an unhandled exception, it is recorded as FAILED
            and wrapped in WatchlistPipelineError before being re-raised.
          - Stages that return SKIPPED are recorded but do not halt the pipeline.

        Returns:
            The mutated WatchlistExecutionContext with all stage_results appended.
        """
        logger.info(
            f"Starting watchlist pipeline execution for run_id={context.run_id} "
            f"with {len(self._stages)} registered stages."
        )

        for stage in self._stages:
            logger.info(f"Executing watchlist stage: {stage.name}")
            start_time = time.perf_counter()

            try:
                result = await stage.execute(context)

                # Enforce contract: every stage must return a WatchlistStageResult.
                if not isinstance(result, WatchlistStageResult):
                    raise WatchlistPipelineError(
                        f"Stage '{stage.name}' did not return a WatchlistStageResult.",
                        details={"stage_name": stage.name, "returned_type": type(result).__name__},
                    )

                context.stage_results.append(result)
                logger.info(
                    f"Stage '{stage.name}' completed with status={result.status.value} "
                    f"in {result.duration_ms:.2f}ms."
                )

                # Fail-fast: halt pipeline on first FAILED stage.
                if result.status == WatchlistStageStatus.FAILED:
                    logger.error(
                        f"Stage '{stage.name}' returned FAILED status. "
                        "Halting watchlist pipeline."
                    )
                    break

            except WatchlistPipelineError:
                # Re-raise pipeline errors without double-wrapping.
                raise

            except Exception as exc:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"Stage '{stage.name}' raised an unhandled exception. "
                    "Halting watchlist pipeline.",
                    exc_info=True,
                )

                # Record the failure in the context before re-raising.
                error_result = WatchlistStageResult(
                    stage_name=stage.name,
                    status=WatchlistStageStatus.FAILED,
                    duration_ms=duration_ms,
                    warnings=[f"Unhandled exception: {str(exc)}"],
                )
                context.stage_results.append(error_result)

                raise WatchlistPipelineError(
                    f"Pipeline execution failed at stage '{stage.name}'.",
                    details={"stage_name": stage.name, "error": str(exc)},
                ) from exc

        logger.info(
            f"Watchlist pipeline execution complete for run_id={context.run_id}. "
            f"Stages executed: {len(context.stage_results)}."
        )
        return context
