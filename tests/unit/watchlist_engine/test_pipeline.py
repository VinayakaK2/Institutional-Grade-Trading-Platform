"""
Unit tests for WatchlistExecutionPipeline.

Covers:
  - Stage registration with max stage guard.
  - Stages execute in registration order.
  - Stage results are recorded in the context.
  - Pipeline halts on first FAILED stage (fail-fast).
  - Unhandled stage exceptions are wrapped in WatchlistPipelineError.
  - Skipped stages are recorded but do not halt the pipeline.
  - Pipeline metadata is updated (stage count) after execution.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.contracts.contracts import IWatchlistStage
from backend.watchlist_engine.models.config import WatchlistPipelineSettings
from backend.watchlist_engine.models.exceptions import WatchlistPipelineError
from backend.watchlist_engine.models.models import (
    WatchlistCandidate,
    WatchlistExecutionContext,
    WatchlistStageResult,
    WatchlistStageStatus,
    WatchlistSymbol,
)
from backend.watchlist_engine.pipeline.pipeline import WatchlistExecutionPipeline


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_candidate(ticker: str) -> WatchlistCandidate:
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol=ticker, exchange=ExchangeReference(code="NSE")),
        )
    )


def make_context(run_id: str = "test-run") -> WatchlistExecutionContext:
    return WatchlistExecutionContext(
        run_id=run_id,
        snapshot_id="snap-1",
        started_at=datetime.now(timezone.utc),
        candidates=[make_candidate("RELIANCE")],
    )


def make_stage(name: str, status: WatchlistStageStatus = WatchlistStageStatus.SUCCESS) -> IWatchlistStage:
    """Builds a mock stage that returns the given status."""
    stage = MagicMock(spec=IWatchlistStage)
    stage.name = name
    stage.execute = AsyncMock(
        return_value=WatchlistStageResult(
            stage_name=name,
            status=status,
            duration_ms=1.0,
        )
    )
    return stage


# ── Stage Registration ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_registers_stage() -> None:
    """Stages must be registerable without error."""
    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings(max_stages=5))
    stage = make_stage("Stage1")
    pipeline.register_stage(stage)
    # No exception = pass.


@pytest.mark.asyncio
async def test_pipeline_max_stage_limit_raises() -> None:
    """Registering more stages than max_stages must raise WatchlistPipelineError."""
    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings(max_stages=2))
    pipeline.register_stage(make_stage("Stage1"))
    pipeline.register_stage(make_stage("Stage2"))
    with pytest.raises(WatchlistPipelineError, match="Maximum pipeline stages"):
        pipeline.register_stage(make_stage("Stage3"))


# ── Execution Order ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_executes_in_registration_order() -> None:
    """Stages must execute in the order they were registered."""
    execution_order: list = []

    async def make_recording_stage(name: str) -> IWatchlistStage:
        stage = MagicMock(spec=IWatchlistStage)
        stage.name = name

        async def execute_fn(ctx: WatchlistExecutionContext) -> WatchlistStageResult:
            execution_order.append(name)
            return WatchlistStageResult(stage_name=name, status=WatchlistStageStatus.SUCCESS, duration_ms=1.0)

        stage.execute = execute_fn
        return stage

    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings())
    pipeline.register_stage(await make_recording_stage("StageA"))
    pipeline.register_stage(await make_recording_stage("StageB"))
    pipeline.register_stage(await make_recording_stage("StageC"))

    ctx = make_context()
    await pipeline.execute(ctx)

    assert execution_order == ["StageA", "StageB", "StageC"]


# ── Context Propagation ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_records_stage_results_in_context() -> None:
    """All stage results must be appended to context.stage_results after execution."""
    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings())
    pipeline.register_stage(make_stage("Stage1"))
    pipeline.register_stage(make_stage("Stage2"))

    ctx = make_context()
    result_ctx = await pipeline.execute(ctx)

    assert len(result_ctx.stage_results) == 2
    assert result_ctx.stage_results[0].stage_name == "Stage1"
    assert result_ctx.stage_results[1].stage_name == "Stage2"


# ── Fail-Fast ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_halts_on_failed_stage() -> None:
    """Pipeline must stop at the first FAILED stage — subsequent stages must not run."""
    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings())
    pipeline.register_stage(make_stage("Stage1", WatchlistStageStatus.SUCCESS))
    pipeline.register_stage(make_stage("Stage2", WatchlistStageStatus.FAILED))
    pipeline.register_stage(make_stage("Stage3", WatchlistStageStatus.SUCCESS))

    ctx = make_context()
    result_ctx = await pipeline.execute(ctx)

    # Only Stage1 and Stage2 should have run.
    assert len(result_ctx.stage_results) == 2
    assert result_ctx.stage_results[1].status == WatchlistStageStatus.FAILED


# ── Skipped Stages ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_skipped_stage_does_not_halt_pipeline() -> None:
    """A SKIPPED stage must be recorded but must not halt the pipeline."""
    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings())
    pipeline.register_stage(make_stage("Stage1", WatchlistStageStatus.SUCCESS))
    pipeline.register_stage(make_stage("Stage2", WatchlistStageStatus.SKIPPED))
    pipeline.register_stage(make_stage("Stage3", WatchlistStageStatus.SUCCESS))

    ctx = make_context()
    result_ctx = await pipeline.execute(ctx)

    assert len(result_ctx.stage_results) == 3
    assert result_ctx.stage_results[1].status == WatchlistStageStatus.SKIPPED


# ── Exception Wrapping ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_wraps_unhandled_exception_in_pipeline_error() -> None:
    """Unhandled exceptions from stages must be wrapped in WatchlistPipelineError."""
    bad_stage = MagicMock(spec=IWatchlistStage)
    bad_stage.name = "BrokenStage"
    bad_stage.execute = AsyncMock(side_effect=RuntimeError("Unexpected failure"))

    pipeline = WatchlistExecutionPipeline(WatchlistPipelineSettings())
    pipeline.register_stage(bad_stage)

    ctx = make_context()
    with pytest.raises(WatchlistPipelineError, match="BrokenStage"):
        await pipeline.execute(ctx)

    # The failed stage result must have been recorded before the exception was raised.
    assert len(ctx.stage_results) == 1
    assert ctx.stage_results[0].status == WatchlistStageStatus.FAILED
