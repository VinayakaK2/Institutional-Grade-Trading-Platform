import pytest

from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest
from backend.trade_validation_engine.signal_aggregation.config.config import SignalAggregationConfig
from backend.trade_validation_engine.signal_aggregation.stages.universe import UniverseAggregationStage, MockUniverseSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.watchlist import WatchlistAggregationStage, MockWatchlistSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.trend import TrendAggregationStage, MockTrendSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.consolidation import ConsolidationAggregationStage, MockConsolidationSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.liquidity_grab import LiquidityGrabAggregationStage, MockLiquidityGrabSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.assembly import EvidenceAssemblyStage
from backend.trade_validation_engine.signal_aggregation.di.container import MockQueryService

@pytest.fixture
def base_request():
    return SignalAggregationRequest(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        universe_snapshot_version=1, watchlist_snapshot_version=1,
        trend_snapshot_version=1, consolidation_snapshot_version=1,
        liquidity_grab_snapshot_version=1,
        configuration=SignalAggregationConfig(fail_fast=False)
    )

@pytest.mark.asyncio
async def test_universe_stage(base_request):
    stage = UniverseAggregationStage(MockQueryService(MockUniverseSnapshot()))
    result = await stage.execute(base_request, {})
    assert result.success is True
    assert result.evidence.universe_state == "ACTIVE"

@pytest.mark.asyncio
async def test_watchlist_stage(base_request):
    stage = WatchlistAggregationStage(MockQueryService(MockWatchlistSnapshot()))
    result = await stage.execute(base_request, {})
    assert result.success is True
    assert result.evidence.watchlist_state == "WATCHED"

@pytest.mark.asyncio
async def test_trend_stage(base_request):
    stage = TrendAggregationStage(MockQueryService(MockTrendSnapshot()))
    result = await stage.execute(base_request, {})
    assert result.success is True
    assert result.evidence.trend_state == "UPTREND"

@pytest.mark.asyncio
async def test_consolidation_stage(base_request):
    stage = ConsolidationAggregationStage(MockQueryService(MockConsolidationSnapshot()))
    result = await stage.execute(base_request, {})
    assert result.success is True
    assert result.evidence.consolidation_state == "BREAKOUT"

@pytest.mark.asyncio
async def test_liquidity_grab_stage(base_request):
    stage = LiquidityGrabAggregationStage(MockQueryService(MockLiquidityGrabSnapshot()))
    result = await stage.execute(base_request, {})
    assert result.success is True
    assert result.evidence.liquidity_grab_state == "DETECTED"

@pytest.mark.asyncio
async def test_stages_snapshot_not_found(base_request):
    stage = UniverseAggregationStage(MockQueryService(None))
    result = await stage.execute(base_request, {})
    assert result.success is False
    assert "not found" in result.error_message
    
    stage_w = WatchlistAggregationStage(MockQueryService(None))
    result_w = await stage_w.execute(base_request, {})
    assert result_w.success is False
    assert "not found" in result_w.error_message

    stage_t = TrendAggregationStage(MockQueryService(None))
    result_t = await stage_t.execute(base_request, {})
    assert result_t.success is False
    assert "not found" in result_t.error_message

    stage_c = ConsolidationAggregationStage(MockQueryService(None))
    result_c = await stage_c.execute(base_request, {})
    assert result_c.success is False
    assert "not found" in result_c.error_message

    stage_lg = LiquidityGrabAggregationStage(MockQueryService(None))
    result_lg = await stage_lg.execute(base_request, {})
    assert result_lg.success is False
    assert "not found" in result_lg.error_message

@pytest.mark.asyncio
async def test_assembly_stage_success(base_request):
    # Populate mock pipeline state
    pipeline_state = {
        "UniverseAggregationStage": await UniverseAggregationStage(MockQueryService(MockUniverseSnapshot())).execute(base_request, {}),
        "WatchlistAggregationStage": await WatchlistAggregationStage(MockQueryService(MockWatchlistSnapshot())).execute(base_request, {}),
        "TrendAggregationStage": await TrendAggregationStage(MockQueryService(MockTrendSnapshot())).execute(base_request, {}),
        "ConsolidationAggregationStage": await ConsolidationAggregationStage(MockQueryService(MockConsolidationSnapshot())).execute(base_request, {}),
        "LiquidityGrabAggregationStage": await LiquidityGrabAggregationStage(MockQueryService(MockLiquidityGrabSnapshot())).execute(base_request, {})
    }
    
    stage = EvidenceAssemblyStage()
    result = await stage.execute(base_request, pipeline_state)
    assert result.success is True
    assert result.evidence.symbol == "BTCUSD"
    assert result.evidence.universe_evidence.universe_state == "ACTIVE"
    assert result.evidence.watchlist_evidence.watchlist_state == "WATCHED"
    assert result.evidence.trend_evidence.trend_state == "UPTREND"
    assert result.evidence.consolidation_evidence.consolidation_state == "BREAKOUT"
    assert result.evidence.liquidity_grab_evidence.liquidity_grab_state == "DETECTED"

@pytest.mark.asyncio
async def test_assembly_stage_missing_dependencies(base_request):
    pipeline_state = {
        "UniverseAggregationStage": await UniverseAggregationStage(MockQueryService(None)).execute(base_request, {})
    }
    
    stage = EvidenceAssemblyStage()
    result = await stage.execute(base_request, pipeline_state)
    assert result.success is False
    assert "Universe" in result.error_message
    assert "Watchlist" in result.error_message
