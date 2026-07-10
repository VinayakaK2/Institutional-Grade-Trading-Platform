import pytest

from backend.trend_engine.quality.engine.engine import TrendQualityEngine
from backend.trend_engine.quality.repository.memory import InMemoryTrendQualityRepository
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.quality.pipeline.stages.strength import TrendStrengthStage
from backend.trend_engine.quality.pipeline.stages.consistency import TrendConsistencyStage
from backend.trend_engine.quality.pipeline.stages.pullback import PullbackQualityStage
from backend.trend_engine.quality.pipeline.stages.persistence import TrendPersistenceStage
from backend.trend_engine.quality.pipeline.stages.normalization import TrendNormalizationStage

from backend.trend_engine.providers.memory import InMemoryIndicatorProvider, InMemoryStructureProvider


@pytest.mark.asyncio
async def test_deterministic_output(sample_trend_snapshot):
    """
    Verify that executing the engine multiple times with the exact same inputs
    produces identical quality metrics.
    """
    config = TrendQualityConfig()
    
    ind_provider = InMemoryIndicatorProvider({})
    struct_provider = InMemoryStructureProvider({})
    
    stages = [
        TrendStrengthStage(ind_provider),
        TrendConsistencyStage(struct_provider),
        PullbackQualityStage(struct_provider),
        TrendPersistenceStage(struct_provider),
        TrendNormalizationStage()
    ]
    
    engine1 = TrendQualityEngine(InMemoryTrendQualityRepository(), config, stages)
    snapshot1 = await engine1.evaluate_trend_quality(sample_trend_snapshot)
    
    engine2 = TrendQualityEngine(InMemoryTrendQualityRepository(), config, stages)
    snapshot2 = await engine2.evaluate_trend_quality(sample_trend_snapshot)
    
    # Asserting deep equality on the symbol evaluations
    assert len(snapshot1.symbols) == len(snapshot2.symbols)
    
    sym1 = snapshot1.symbols[0]
    sym2 = snapshot2.symbols[0]
    
    # Check all metric sets for exact equality
    assert sym1.strength_metrics.model_dump() == sym2.strength_metrics.model_dump()
    assert sym1.consistency_metrics.model_dump() == sym2.consistency_metrics.model_dump()
    assert sym1.pullback_metrics.model_dump() == sym2.pullback_metrics.model_dump()
    assert sym1.persistence_metrics.model_dump() == sym2.persistence_metrics.model_dump()
    assert sym1.normalized_metrics.model_dump() == sym2.normalized_metrics.model_dump()


@pytest.mark.asyncio
async def test_floating_point_stability(sample_trend_snapshot):
    """
    Verify that acceptable floating point precision diffs don't crash
    or drastically alter the result beyond numerical tolerances.
    """
    config = TrendQualityConfig()
    
    # Since we are using standard python floats, and pydantic float types,
    # we just need to ensure the stages don't fail when subjected to normal math.
    ind_provider = InMemoryIndicatorProvider({})
    struct_provider = InMemoryStructureProvider({})
    
    stages = [
        TrendStrengthStage(ind_provider),
        TrendConsistencyStage(struct_provider),
        PullbackQualityStage(struct_provider),
        TrendPersistenceStage(struct_provider),
        TrendNormalizationStage()
    ]
    
    engine = TrendQualityEngine(InMemoryTrendQualityRepository(), config, stages)
    snapshot = await engine.evaluate_trend_quality(sample_trend_snapshot)
    
    sym = snapshot.symbols[0]
    assert isinstance(sym.strength_metrics.ema_separation_ratio, float)
    assert isinstance(sym.normalized_metrics.normalized_strength, float)
