import pytest
from backend.trend_engine.lifecycle.pipeline.stages.validation import LifecycleValidationStage
from backend.trend_engine.lifecycle.pipeline.stages.continuation import ContinuationEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.weakening import WeakeningEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.break_eval import BreakEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.end_eval import EndEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.aggregation import AggregationEvaluationStage

from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext, SymbolLifecycleContext
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState, ContinuationEvidence, WeakeningEvidence, BreakEvidence, EndEvidence
from backend.trend_engine.lifecycle.exceptions import LifecycleEvaluationError
from backend.trend_engine.lifecycle.config.config import TrendLifecycleConfig

# We will need some mock parent snapshots. I will use the ones we have in other tests or create minimal mocks.
from backend.trend_engine.models.models import TrendSnapshot, TrendSymbol, TrendDirection, TrendState
from backend.trend_engine.quality.models.models import TrendQualitySnapshot, TrendQualitySymbolResult, NormalizedQualityMetrics, TrendConsistencyResult, TrendStrengthResult, PullbackQualityResult, TrendPersistenceResult
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

@pytest.fixture
def mock_snapshots():
    sym = WatchlistSymbol(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        market_segment="UNKNOWN",
        instrument_type="UNKNOWN"
    )
    ts = TrendSnapshot(
        snapshot_id="t_1",
        snapshot_version=1,
        source_watchlist_snapshot_id="w_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="i_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s_1",
        source_structure_snapshot_version=1,
        symbols=[
            TrendSymbol(
                watchlist_symbol=sym,
                direction=TrendDirection.UPTREND,
                state=TrendState.VALID
            )
        ],
        pipeline_version="1.0",
        configuration_hash="hash",
        schema_version="1.0",
        execution_metadata={},
        audit_metadata={},
        created_at="2026-07-09T00:00:00Z"
    )
    
    qs = TrendQualitySnapshot(
        quality_snapshot_id="q_1",
        source_trend_snapshot_id="t_1",
        symbols=[
            TrendQualitySymbolResult(
                symbol_key="AAPL:NASDAQ",
                strength_metrics=TrendStrengthResult(ema_separation_ratio=0.03, direction_stability_percent=100.0, is_extended=False),
                consistency_metrics=TrendConsistencyResult(valid_structures_count=0, sequence_stability_ratio=1.0, structural_noise_percent=10.0),
                pullback_metrics=PullbackQualityResult(average_pullback_depth_percent=5.0, deepest_pullback_percent=8.0, pullback_count=2, average_pullback_duration_bars=3.0),
                persistence_metrics=TrendPersistenceResult(trend_age_bars=10, longest_uninterrupted_run_bars=10, interruption_count=0),
                normalized_metrics=NormalizedQualityMetrics(normalized_strength=0.8, normalized_consistency=1.0, normalized_pullback_quality=0.5, normalized_persistence=0.5)
            )
        ],
        pipeline_version="1.0",
        configuration_hash="hash",
        quality_algorithm_version="1.0",
        metadata={
            "pipeline_version": "1.0",
            "configuration_hash": "hash",
            "configuration_version": 1,
            "quality_algorithm_version": "1.0",
            "evaluation_timestamp": "2026-07-09T00:00:00Z",
            "evaluation_duration_ms": 10.0
        }
    )
    
    return ts, qs

@pytest.fixture
def context(mock_snapshots):
    ts, qs = mock_snapshots
    config = TrendLifecycleConfig()
    return LifecycleExecutionContext(
        config=config,
        trend_snapshot=ts,
        quality_snapshot=qs
    )

@pytest.mark.asyncio
async def test_validation_stage(context):
    stage = LifecycleValidationStage()
    await stage.execute(context)
    assert "AAPL:NASDAQ" in context.symbol_contexts

@pytest.mark.asyncio
async def test_validation_mismatch(context):
    context.trend_snapshot = context.trend_snapshot.model_copy(update={"snapshot_id": "t_2"})
    stage = LifecycleValidationStage()
    with pytest.raises(LifecycleEvaluationError):
        await stage.execute(context)

@pytest.mark.asyncio
async def test_continuation_stage(context):
    # Pre-populate symbol contexts (simulating validation stage)
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    stage = ContinuationEvaluationStage()
    await stage.execute(context)
    
    ev = context.symbol_contexts["AAPL:NASDAQ"].continuation_evidence
    assert ev is not None
    assert ev.is_continuing is True

@pytest.mark.asyncio
async def test_weakening_stage(context):
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    
    # modify config so separation ratio triggers weakening
    context.config.weakening_ema_separation_ratio_threshold = 5.0 # 5%
    
    stage = WeakeningEvaluationStage()
    await stage.execute(context)
    
    ev = context.symbol_contexts["AAPL:NASDAQ"].weakening_evidence
    assert ev is not None
    assert ev.is_weakening is True

@pytest.mark.asyncio
async def test_break_stage(context):
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    
    # invalidate structure
    qs = context.quality_snapshot.symbols[0]
    context.quality_snapshot = context.quality_snapshot.model_copy(
        update={
            "symbols": [
                qs.model_copy(
                    update={
                        "consistency_metrics": qs.consistency_metrics.model_copy(
                            update={"structural_noise_percent": 100.0}
                        )
                    }
                )
            ]
        }
    )
    
    stage = BreakEvaluationStage()
    await stage.execute(context)
    
    ev = context.symbol_contexts["AAPL:NASDAQ"].break_evidence
    assert ev is not None
    assert ev.is_broken is True

@pytest.mark.asyncio
async def test_end_stage(context):
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    
    ts = context.trend_snapshot.symbols[0]
    # We can't mutate Pydantic frozen model directly, we must replace it.
    context.trend_snapshot = context.trend_snapshot.model_copy(
        update={
            "symbols": [
                ts.model_copy(update={"direction": TrendDirection.SIDEWAYS})
            ]
        }
    )
    
    stage = EndEvaluationStage()
    await stage.execute(context)
    
    ev = context.symbol_contexts["AAPL:NASDAQ"].end_evidence
    assert ev is not None
    assert ev.is_ended is True

@pytest.mark.asyncio
async def test_aggregation_stage(context):
    sym_ctx = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    
    # Mix evidences: Weakening and Break are true
    sym_ctx.continuation_evidence = ContinuationEvidence(is_continuing=False, reason="")
    sym_ctx.weakening_evidence = WeakeningEvidence(is_weakening=True, reason="")
    sym_ctx.break_evidence = BreakEvidence(is_broken=True, reason="")
    sym_ctx.end_evidence = EndEvidence(is_ended=False, reason="")
    
    context.symbol_contexts["AAPL:NASDAQ"] = sym_ctx
    
    stage = AggregationEvaluationStage()
    await stage.execute(context)
    
    assert sym_ctx.final_state == TrendLifecycleState.BROKEN

@pytest.mark.asyncio
async def test_aggregation_ended_transition(context):
    stage = AggregationEvaluationStage()
    
    # Pre-populate with ENDED evidence
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    context.symbol_contexts["AAPL:NASDAQ"].end_evidence = EndEvidence(is_ended=True, reason="test")
    context.symbol_contexts["AAPL:NASDAQ"].break_evidence = BreakEvidence(is_broken=False, reason="")
    context.symbol_contexts["AAPL:NASDAQ"].weakening_evidence = WeakeningEvidence(is_weakening=False, reason="")
    context.symbol_contexts["AAPL:NASDAQ"].continuation_evidence = ContinuationEvidence(is_continuing=False, reason="")
    
    await stage.execute(context)
    assert context.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.ENDED

@pytest.mark.asyncio
async def test_aggregation_active_transition(context):
    stage = AggregationEvaluationStage()
    
    # Pre-populate with NO evidence
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    context.symbol_contexts["AAPL:NASDAQ"].end_evidence = EndEvidence(is_ended=False, reason="")
    context.symbol_contexts["AAPL:NASDAQ"].break_evidence = BreakEvidence(is_broken=False, reason="")
    context.symbol_contexts["AAPL:NASDAQ"].weakening_evidence = WeakeningEvidence(is_weakening=False, reason="")
    context.symbol_contexts["AAPL:NASDAQ"].continuation_evidence = ContinuationEvidence(is_continuing=False, reason="")
    
    await stage.execute(context)
    assert context.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.ACTIVE

@pytest.mark.asyncio
async def test_aggregation_missing_evidence(context):
    stage = AggregationEvaluationStage()
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    # Leave evidence as None
    
    await stage.execute(context)
    # Missing evidence defaults to ACTIVE
    assert context.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.ACTIVE
    
@pytest.mark.asyncio
async def test_stages_missing_quality_snapshot(context):
    # Test missing quality snapshot logic in stages
    context.quality_snapshot = context.quality_snapshot.model_copy(update={"symbols": []})
    context.symbol_contexts["AAPL:NASDAQ"] = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
    
    for stage in [ContinuationEvaluationStage(), WeakeningEvaluationStage(), BreakEvaluationStage(), EndEvaluationStage()]:
        await stage.execute(context)
        # Should cleanly continue without error
        assert "AAPL:NASDAQ" in context.symbol_contexts
