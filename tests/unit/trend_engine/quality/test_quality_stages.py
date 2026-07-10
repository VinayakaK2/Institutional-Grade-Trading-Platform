import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

from backend.trend_engine.quality.pipeline.stages.strength import TrendStrengthStage
from backend.trend_engine.quality.pipeline.stages.consistency import TrendConsistencyStage
from backend.trend_engine.quality.pipeline.stages.pullback import PullbackQualityStage
from backend.trend_engine.quality.pipeline.stages.persistence import TrendPersistenceStage
from backend.trend_engine.quality.pipeline.stages.normalization import TrendNormalizationStage
from backend.trend_engine.quality.models.models import (
    TrendStrengthResult,
    TrendConsistencyResult,
    PullbackQualityResult,
    TrendPersistenceResult
)
from backend.trend_engine.providers.memory import InMemoryIndicatorProvider, InMemoryStructureProvider
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType




@pytest.mark.asyncio
async def test_strength_stage(context):
    indicator_data = {
        "AAPL:NASDAQ": {
            20: IndicatorResult(dataset_version="1", timeframe="1d", timestamp=datetime.now(), symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), indicator_type=IndicatorType.EMA, parameters={"period": 20}, value=110.0),
            50: IndicatorResult(dataset_version="1", timeframe="1d", timestamp=datetime.now(), symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), indicator_type=IndicatorType.EMA, parameters={"period": 50}, value=105.0),
            200: IndicatorResult(dataset_version="1", timeframe="1d", timestamp=datetime.now(), symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), indicator_type=IndicatorType.EMA, parameters={"period": 200}, value=100.0)
        }
    }
    provider = InMemoryIndicatorProvider(indicator_data)
    stage = TrendStrengthStage(provider)
    
    await stage.execute(context)
    
    res = context.symbol_contexts["AAPL:NASDAQ"].strength_result
    assert res is not None
    assert res.ema_separation_ratio == 0.1  # (110 - 100) / 100 = 0.1
    assert res.direction_stability_percent == 100.0
    assert res.is_extended is True # Because > 0.05 default max

@pytest.mark.asyncio
async def test_consistency_and_pullback_stages(context):
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
    
    structures_data = {
        "AAPL:NASDAQ": [
            MarketStructurePoint(id="1", swing_point=SwingPoint(type=SwingType.HIGH, price=120.0, timestamp=datetime.fromtimestamp(base_time + 86400 * 3, tz=timezone.utc), candle_high=120.0, candle_low=110.0, candle_open=115.0, candle_close=118.0), type=StructureType.HH),
            MarketStructurePoint(id="2", swing_point=SwingPoint(type=SwingType.LOW, price=110.0, timestamp=datetime.fromtimestamp(base_time + 86400 * 2, tz=timezone.utc), candle_high=115.0, candle_low=110.0, candle_open=112.0, candle_close=111.0), type=StructureType.HL),
            MarketStructurePoint(id="3", swing_point=SwingPoint(type=SwingType.HIGH, price=115.0, timestamp=datetime.fromtimestamp(base_time + 86400 * 1, tz=timezone.utc), candle_high=115.0, candle_low=105.0, candle_open=110.0, candle_close=112.0), type=StructureType.HH),
            MarketStructurePoint(id="4", swing_point=SwingPoint(type=SwingType.LOW, price=100.0, timestamp=datetime.fromtimestamp(base_time, tz=timezone.utc), candle_high=105.0, candle_low=100.0, candle_open=102.0, candle_close=101.0), type=StructureType.HL),
        ]
    }
    provider = InMemoryStructureProvider(structures_data)
    
    c_stage = TrendConsistencyStage(provider)
    await c_stage.execute(context)
    c_res = context.symbol_contexts["AAPL:NASDAQ"].consistency_result
    assert c_res is not None
    assert c_res.valid_structures_count > 0

    p_stage = PullbackQualityStage(provider)
    await p_stage.execute(context)
    p_res = context.symbol_contexts["AAPL:NASDAQ"].pullback_result
    assert p_res is not None
    assert p_res.pullback_count > 0

    per_stage = TrendPersistenceStage(provider)
    await per_stage.execute(context)
    per_res = context.symbol_contexts["AAPL:NASDAQ"].persistence_result
    assert per_res is not None
    assert per_res.longest_uninterrupted_run_bars > 0

@pytest.mark.asyncio
async def test_normalization_stage(context):
    ctx = context.symbol_contexts["AAPL:NASDAQ"]
    # Mock prior stage outputs
    ctx.strength_result = TrendStrengthResult(ema_separation_ratio=0.02, direction_stability_percent=100.0, is_extended=False)
    ctx.consistency_result = TrendConsistencyResult(sequence_stability_ratio=0.8, structural_noise_percent=20.0, valid_structures_count=5)
    ctx.pullback_result = PullbackQualityResult(average_pullback_depth_percent=5.0, average_pullback_duration_bars=3.0, pullback_count=2, deepest_pullback_percent=7.0)
    ctx.persistence_result = TrendPersistenceResult(trend_age_bars=10, interruption_count=1, longest_uninterrupted_run_bars=5)
    
    stage = TrendNormalizationStage()
    await stage.execute(context)
    
    norm = ctx.normalized_metrics
    assert norm is not None
    assert 0.0 <= norm.normalized_strength <= 1.0
    assert 0.0 <= norm.normalized_consistency <= 1.0
    assert 0.0 <= norm.normalized_pullback_quality <= 1.0
    assert 0.0 <= norm.normalized_persistence <= 1.0
