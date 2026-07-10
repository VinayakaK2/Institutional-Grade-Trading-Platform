import pytest
import copy
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext, SymbolLifecycleContext
from backend.trend_engine.lifecycle.pipeline.stages.aggregation import AggregationEvaluationStage
from backend.trend_engine.lifecycle.models.models import (
    TrendLifecycleState, 
    ContinuationEvidence, 
    WeakeningEvidence, 
    BreakEvidence, 
    EndEvidence
)
from backend.trend_engine.lifecycle.config.config import TrendLifecycleConfig

# Re-use fixtures
from tests.unit.trend_engine.lifecycle.test_lifecycle_stages import mock_snapshots  # noqa: F401
from tests.unit.trend_engine.lifecycle.test_lifecycle_engine import engine  # noqa: F401

@pytest.mark.asyncio
async def test_regression_determinism(engine, mock_snapshots):
    """
    Verify that identical parent snapshots and config produce identical 
    TrendLifecycleSnapshot outputs (excluding metadata timestamps and dynamically generated IDs like snapshot_version if it increments).
    """
    ts1, qs1 = mock_snapshots
    
    # We copy them to simulate independent runs
    ts2 = copy.deepcopy(ts1)
    qs2 = copy.deepcopy(qs1)
    
    # Clear the memory repository before each run so version is identical
    engine._repository._snapshots.clear()
    engine._repository._latest_by_parent.clear()
    
    snap1 = await engine.evaluate_lifecycle(ts1, qs1)
    
    engine._repository._snapshots.clear()
    engine._repository._latest_by_parent.clear()
    
    snap2 = await engine.evaluate_lifecycle(ts2, qs2)
    
    assert snap1.snapshot_id == snap2.snapshot_id
    assert snap1.configuration_hash == snap2.configuration_hash
    assert snap1.symbols["AAPL:NASDAQ"].final_state == snap2.symbols["AAPL:NASDAQ"].final_state
    
    # They should be functionally identical
    dict1 = snap1.model_dump(exclude={"metadata", "execution_metadata"})
    dict2 = snap2.model_dump(exclude={"metadata", "execution_metadata"})
    
    assert dict1 == dict2

@pytest.mark.asyncio
async def test_regression_immutability(engine, mock_snapshots):
    """
    Verify that TrendLifecycleEngine never mutates the parent TrendSnapshot 
    or TrendQualitySnapshot.
    """
    ts, qs = mock_snapshots
    
    ts_original = copy.deepcopy(ts)
    qs_original = copy.deepcopy(qs)
    
    await engine.evaluate_lifecycle(ts, qs)
    
    assert ts.model_dump() == ts_original.model_dump()
    assert qs.model_dump() == qs_original.model_dump()

@pytest.mark.asyncio
async def test_regression_aggregation_stability(mock_snapshots):
    """
    Given identical evidence:
    Continuation, Weakening, Break, End
    Aggregation must always return the same lifecycle state (protects against precedence changes).
    """
    ts, qs = mock_snapshots
    config = TrendLifecycleConfig()
    stage = AggregationEvaluationStage()
    
    def create_ctx(ce, we, be, ee):
        ctx = LifecycleExecutionContext(config=config, trend_snapshot=ts, quality_snapshot=qs)
        sym = SymbolLifecycleContext(symbol_key="AAPL:NASDAQ")
        sym.continuation_evidence = ContinuationEvidence(is_continuing=ce, reason="")
        sym.weakening_evidence = WeakeningEvidence(is_weakening=we, reason="")
        sym.break_evidence = BreakEvidence(is_broken=be, reason="")
        sym.end_evidence = EndEvidence(is_ended=ee, reason="")
        ctx.symbol_contexts["AAPL:NASDAQ"] = sym
        return ctx
        
    # Test 1: All True -> ENDED (highest priority)
    ctx1 = create_ctx(True, True, True, True)
    await stage.execute(ctx1)
    assert ctx1.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.ENDED
    
    # Test 2: User explicit case: Continuation=True, Weakening=True, Break=False, End=False -> WEAKENING
    ctx2_weakening = create_ctx(True, True, False, False)
    await stage.execute(ctx2_weakening)
    assert ctx2_weakening.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.WEAKENING
    
    # Test 3: Weakening + Break -> BROKEN
    ctx2 = create_ctx(False, True, True, False)
    await stage.execute(ctx2)
    assert ctx2.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.BROKEN
    
    # Test 3: Continuation + Weakening -> WEAKENING
    ctx3 = create_ctx(True, True, False, False)
    await stage.execute(ctx3)
    assert ctx3.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.WEAKENING
    
    # Test 4: Only Continuation -> CONTINUING
    ctx4 = create_ctx(True, False, False, False)
    await stage.execute(ctx4)
    assert ctx4.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.CONTINUING
    
    # Test 5: None -> ACTIVE
    ctx5 = create_ctx(False, False, False, False)
    await stage.execute(ctx5)
    assert ctx5.symbol_contexts["AAPL:NASDAQ"].final_state == TrendLifecycleState.ACTIVE
