import pytest
from datetime import datetime, timezone

from backend.universe_engine.liquidity.models import LiquidityFilterConfiguration
from backend.universe_engine.liquidity.stages import (
    AverageDailyVolumeFilter,
    AverageDailyTurnoverFilter,
    MinimumPriceFilter,
    MinimumMarketCapFilter
)
from backend.universe_engine.liquidity.pipeline import LiquidityFilterPipeline
from backend.universe_engine.liquidity.engine import LiquidityFilterEngine
from backend.universe_engine.liquidity.repository import InMemoryLiquidityRepository
from backend.universe_engine.models.universe import UniverseSnapshot, ValidationStatus

@pytest.fixture
def config():
    return LiquidityFilterConfiguration(
        volume_lookback_days=30,
        min_average_daily_volume=500_000,
        turnover_lookback_days=30,
        min_average_daily_turnover=1_000_000.0,
        price_lookback_days=1,
        min_close_price=5.0,
        min_market_capitalization=50_000_000.0
    )

@pytest.fixture
def test_snapshot(create_test_instrument):
    instruments = [
        create_test_instrument("PASS_1"),
        create_test_instrument("FAIL_VOL_1"),
        create_test_instrument("FAIL_TURN_1"),
        create_test_instrument("FAIL_PRICE_1"),
        create_test_instrument("MISSING_CANDLES_1"),
        create_test_instrument("FAIL_MCAP_1"),
        create_test_instrument("MISSING_MCAP_1")
    ]
    return UniverseSnapshot(
        snapshot_id="parent_snapshot_123",
        version=1,
        provider="TEST_PROVIDER",
        symbol_count=len(instruments),
        instruments=instruments,
        metadata={},
        pipeline_version="1.0.0",
        validation_status=ValidationStatus.PASSED,
        created_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_liquidity_filter_engine_orchestration(
    config, 
    test_snapshot, 
    mock_data_provider, 
    mock_fundamental_provider
):
    # Setup Pipeline
    pipeline = LiquidityFilterPipeline()
    pipeline.register_stage(AverageDailyVolumeFilter())
    pipeline.register_stage(AverageDailyTurnoverFilter())
    pipeline.register_stage(MinimumPriceFilter())
    pipeline.register_stage(MinimumMarketCapFilter())
    
    # Setup Engine
    repository = InMemoryLiquidityRepository()
    engine = LiquidityFilterEngine(
        config=config,
        pipeline=pipeline,
        data_provider=mock_data_provider,
        fundamental_provider=mock_fundamental_provider,
        repository=repository,
        pipeline_version="1.1.0"
    )
    
    # Execute
    result = await engine.generate_liquidity_universe(
        run_id="run_abc", 
        parent_snapshot=test_snapshot
    )
    
    universe = result.universe
    
    # Lineage Verification
    assert universe.liquidity_universe_id is not None
    assert universe.parent_snapshot_id == "parent_snapshot_123"
    assert universe.pipeline_version == "1.1.0"
    assert universe.config_hash == engine._hash_config()
    
    # Qualification Verification
    # Only PASS_1 should survive all filters
    assert len(universe.qualified_symbols) == 1
    assert universe.qualified_symbols[0].symbol.symbol == "PASS_1"
    
    # Rejection Verification
    assert len(universe.rejected_symbols) == 6
    
    # Statistics Verification
    assert universe.statistics.initial_instrument_count == 7
    assert universe.statistics.final_qualified_count == 1
    assert universe.statistics.volume_rejections == 1
    assert universe.statistics.turnover_rejections == 1
    assert universe.statistics.price_rejections == 1
    assert universe.statistics.market_cap_rejections == 1
    assert universe.statistics.missing_data_rejections == 2 # missing candles + missing mcap
    assert universe.statistics.processing_time_ms > 0
    
    # Repository Verification
    loaded = await repository.load_liquidity_universe(universe.liquidity_universe_id)
    assert loaded is not None
    assert loaded.parent_snapshot_id == "parent_snapshot_123"
