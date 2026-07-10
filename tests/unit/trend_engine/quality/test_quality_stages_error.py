import pytest
from datetime import datetime, timezone
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.providers.memory import InMemoryIndicatorProvider, InMemoryStructureProvider
from backend.trend_engine.quality.pipeline.stages.strength import TrendStrengthStage
from backend.trend_engine.quality.pipeline.stages.consistency import TrendConsistencyStage
from backend.trend_engine.quality.pipeline.stages.pullback import PullbackQualityStage
from backend.trend_engine.quality.pipeline.stages.persistence import TrendPersistenceStage
from backend.trend_engine.quality.pipeline.stages.normalization import TrendNormalizationStage

class FailingIndicatorProvider(InMemoryIndicatorProvider):
    async def get_ema_indicators(self, symbol, snapshot_id, periods):
        raise ValueError("Simulated indicator failure")

class FailingStructureProvider(InMemoryStructureProvider):
    async def get_latest_structures(self, symbol, snapshot_id, limit=2):
        raise ValueError("Simulated structure failure")

@pytest.fixture
def context(sample_trend_snapshot: TrendSnapshot) -> QualityExecutionContext:
    config = TrendQualityConfig()
    return QualityExecutionContext(parent_snapshot=sample_trend_snapshot, config=config)

@pytest.mark.asyncio
async def test_stages_error_handling(context):
    ind_provider = FailingIndicatorProvider()
    struct_provider = FailingStructureProvider()
    
    stages = [
        TrendStrengthStage(ind_provider),
        TrendConsistencyStage(struct_provider),
        PullbackQualityStage(struct_provider),
        TrendPersistenceStage(struct_provider),
        TrendNormalizationStage()
    ]
    
    for stage in stages:
        # execute should catch the exception and append to context.warnings
        await stage.execute(context)
        
    assert len(context.warnings) >= 4
    
    sym_ctx = context.symbol_contexts["AAPL:NASDAQ"]
    
    # Defaults should be set to 0.0 or equivalent
    assert sym_ctx.strength_result.ema_separation_ratio == 0.0
    assert sym_ctx.consistency_result.sequence_stability_ratio == 0.0
    assert sym_ctx.pullback_result.average_pullback_depth_percent == 0.0
    assert sym_ctx.persistence_result.trend_age_bars == 0
    assert sym_ctx.normalized_metrics.normalized_strength == 0.0
