import pytest
from datetime import datetime, timezone
from backend.universe_engine.liquidity.models import LiquidityFilterContext, LiquidityFilterConfiguration
from backend.universe_engine.liquidity.stages import (
    AverageDailyVolumeFilter,
    AverageDailyTurnoverFilter,
    MinimumPriceFilter,
    MinimumMarketCapFilter
)
from backend.universe_engine.liquidity.models import LiquidityRejectionReason

@pytest.fixture
def context(create_test_instrument):
    config = LiquidityFilterConfiguration(
        volume_lookback_days=30,
        min_average_daily_volume=500_000,
        turnover_lookback_days=30,
        min_average_daily_turnover=1_000_000.0,
        price_lookback_days=1,
        min_close_price=5.0,
        min_market_capitalization=50_000_000.0
    )
    instruments = [
        create_test_instrument("PASS_1"),
        create_test_instrument("FAIL_VOL_1"),
        create_test_instrument("FAIL_TURN_1"),
        create_test_instrument("FAIL_PRICE_1"),
        create_test_instrument("MISSING_CANDLES_1"),
        create_test_instrument("BOUNDARY_VOL_1"),
        create_test_instrument("FAIL_MCAP_1"),
        create_test_instrument("MISSING_MCAP_1")
    ]
    return LiquidityFilterContext(
        run_id="test_run",
        parent_snapshot_id="test_parent",
        config=config,
        qualified_instruments=instruments,
        started_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_average_daily_volume_filter(context, mock_data_provider, mock_fundamental_provider):
    stage = AverageDailyVolumeFilter()
    await stage.execute(context, mock_data_provider, mock_fundamental_provider)
    
    qualified_symbols = [inst.symbol.symbol for inst in context.qualified_instruments]
    rejected_symbols = [rej.instrument_symbol for rej in context.rejected_details]
    
    assert "PASS_1" in qualified_symbols
    assert "BOUNDARY_VOL_1" in qualified_symbols
    assert "FAIL_VOL_1" not in qualified_symbols
    assert "FAIL_VOL_1" in rejected_symbols
    assert "MISSING_CANDLES_1" not in qualified_symbols
    assert "MISSING_CANDLES_1" in rejected_symbols
    
    # Check rejection reasons
    vol_rejections = [r for r in context.rejected_details if r.instrument_symbol == "FAIL_VOL_1"]
    assert len(vol_rejections) == 1
    assert vol_rejections[0].reason == LiquidityRejectionReason.VOLUME_BELOW_THRESHOLD
    
    missing_rejections = [r for r in context.rejected_details if r.instrument_symbol == "MISSING_CANDLES_1"]
    assert len(missing_rejections) == 1
    assert missing_rejections[0].reason == LiquidityRejectionReason.MISSING_DATA

@pytest.mark.asyncio
async def test_average_daily_turnover_filter(context, mock_data_provider, mock_fundamental_provider):
    stage = AverageDailyTurnoverFilter()
    await stage.execute(context, mock_data_provider, mock_fundamental_provider)
    
    qualified_symbols = [inst.symbol.symbol for inst in context.qualified_instruments]
    
    assert "PASS_1" in qualified_symbols
    assert "FAIL_TURN_1" not in qualified_symbols
    
    turnover_rejections = [r for r in context.rejected_details if r.instrument_symbol == "FAIL_TURN_1"]
    assert turnover_rejections[0].reason == LiquidityRejectionReason.TURNOVER_BELOW_THRESHOLD

@pytest.mark.asyncio
async def test_minimum_price_filter(context, mock_data_provider, mock_fundamental_provider):
    stage = MinimumPriceFilter()
    await stage.execute(context, mock_data_provider, mock_fundamental_provider)
    
    qualified_symbols = [inst.symbol.symbol for inst in context.qualified_instruments]
    
    assert "PASS_1" in qualified_symbols
    assert "FAIL_PRICE_1" not in qualified_symbols
    
    price_rejections = [r for r in context.rejected_details if r.instrument_symbol == "FAIL_PRICE_1"]
    assert price_rejections[0].reason == LiquidityRejectionReason.PRICE_BELOW_THRESHOLD

@pytest.mark.asyncio
async def test_minimum_market_cap_filter(context, mock_data_provider, mock_fundamental_provider):
    stage = MinimumMarketCapFilter()
    await stage.execute(context, mock_data_provider, mock_fundamental_provider)
    
    qualified_symbols = [inst.symbol.symbol for inst in context.qualified_instruments]
    
    assert "PASS_1" in qualified_symbols
    assert "FAIL_MCAP_1" not in qualified_symbols
    assert "MISSING_MCAP_1" not in qualified_symbols
    
    mcap_rejections = [r for r in context.rejected_details if r.instrument_symbol == "FAIL_MCAP_1"]
    assert mcap_rejections[0].reason == LiquidityRejectionReason.MARKET_CAP_BELOW_THRESHOLD
    
    missing_mcap = [r for r in context.rejected_details if r.instrument_symbol == "MISSING_MCAP_1"]
    assert missing_mcap[0].reason == LiquidityRejectionReason.MISSING_DATA
