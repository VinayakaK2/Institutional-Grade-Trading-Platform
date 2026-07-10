import pytest
from backend.trend_engine.lifecycle.config.config import TrendLifecycleConfig
from backend.trend_engine.lifecycle.engine.engine import TrendLifecycleEngine
from backend.trend_engine.lifecycle.repository.memory import InMemoryTrendLifecycleRepository
from backend.trend_engine.lifecycle.pipeline.stages.validation import LifecycleValidationStage
from backend.trend_engine.lifecycle.pipeline.stages.continuation import ContinuationEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.weakening import WeakeningEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.break_eval import BreakEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.end_eval import EndEvaluationStage
from backend.trend_engine.lifecycle.pipeline.stages.aggregation import AggregationEvaluationStage
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState

# Re-use the fixtures from test_lifecycle_stages
from tests.unit.trend_engine.lifecycle.test_lifecycle_stages import mock_snapshots  # noqa: F401

@pytest.fixture
def engine():
    config = TrendLifecycleConfig()
    repo = InMemoryTrendLifecycleRepository()
    stages = [
        LifecycleValidationStage(),
        ContinuationEvaluationStage(),
        WeakeningEvaluationStage(),
        BreakEvaluationStage(),
        EndEvaluationStage(),
        AggregationEvaluationStage()
    ]
    return TrendLifecycleEngine(repo, config, stages)

@pytest.mark.asyncio
async def test_engine_orchestration(engine, mock_snapshots):
    ts, qs = mock_snapshots
    
    snapshot = await engine.evaluate_lifecycle(ts, qs)
    
    assert snapshot.snapshot_id.startswith("l_t_1_")
    assert "AAPL:NASDAQ" in snapshot.symbols
    assert snapshot.symbols["AAPL:NASDAQ"].final_state == TrendLifecycleState.CONTINUING
    
    # Run again to test version bumping and lineage
    snapshot2 = await engine.evaluate_lifecycle(ts, qs)
    assert snapshot2.snapshot_version == 2
    assert snapshot2.snapshot_id == "l_t_1_2"
    
    # Assert repository
    exists = await engine._repository.exists_for_parent_snapshot(ts.snapshot_id)
    assert exists is True
