import pytest

from backend.trend_engine.quality.engine.engine import TrendQualityEngine
from backend.trend_engine.quality.repository.memory import InMemoryTrendQualityRepository
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.quality.pipeline.stages.strength import TrendStrengthStage
from backend.trend_engine.quality.pipeline.stages.consistency import TrendConsistencyStage
from backend.trend_engine.quality.pipeline.stages.pullback import PullbackQualityStage
from backend.trend_engine.quality.pipeline.stages.persistence import TrendPersistenceStage
from backend.trend_engine.quality.pipeline.stages.normalization import TrendNormalizationStage
from backend.trend_engine.quality.exceptions import IncompleteQualityEvaluationError

# Using mock providers that return nothing so we can test the fallback to 0.0 values
from backend.trend_engine.providers.memory import InMemoryIndicatorProvider, InMemoryStructureProvider


@pytest.mark.asyncio
async def test_engine_orchestration_complete(sample_trend_snapshot):
    config = TrendQualityConfig()
    repo = InMemoryTrendQualityRepository()
    
    ind_provider = InMemoryIndicatorProvider({})
    struct_provider = InMemoryStructureProvider({})
    
    stages = [
        TrendStrengthStage(ind_provider),
        TrendConsistencyStage(struct_provider),
        PullbackQualityStage(struct_provider),
        TrendPersistenceStage(struct_provider),
        TrendNormalizationStage()
    ]
    
    engine = TrendQualityEngine(repo, config, stages)
    
    # Execute the engine
    snapshot = await engine.evaluate_trend_quality(sample_trend_snapshot)
    
    assert snapshot is not None
    assert snapshot.source_trend_snapshot_id == sample_trend_snapshot.snapshot_id
    assert len(snapshot.symbols) == 1
    
    # Verify metadata
    assert snapshot.metadata.configuration_version == config.configuration_version
    assert snapshot.metadata.quality_algorithm_version == config.quality_algorithm_version
    
    # Verify it was persisted
    saved_snapshot = await repo.get_quality_snapshot(snapshot.quality_snapshot_id)
    assert saved_snapshot is not None
    
    latest_snapshot = await repo.get_latest_quality_for_trend(sample_trend_snapshot.snapshot_id)
    assert latest_snapshot is not None

@pytest.mark.asyncio
async def test_engine_incomplete_evaluation(sample_trend_snapshot):
    config = TrendQualityConfig()
    repo = InMemoryTrendQualityRepository()
    
    # Only adding strength stage, missing consistency, pullback, persistence, normalization
    # This should trigger IncompleteQualityEvaluationError
    stages = [
        TrendStrengthStage(InMemoryIndicatorProvider({}))
    ]
    
    engine = TrendQualityEngine(repo, config, stages)
    
    with pytest.raises(IncompleteQualityEvaluationError):
        await engine.evaluate_trend_quality(sample_trend_snapshot)
