import pytest
import math
from datetime import datetime, timezone, timedelta
from typing import List

from backend.universe_engine.data_quality.stages import (
    HistoricalDataAvailabilityFilter,
    MissingCandleDetection,
    SuspendedTradingDetection,
    DataCompletenessValidation,
    CorporateActionConsistency,
)
from backend.universe_engine.data_quality.models import (
    DataQualityFilterContext,
    DataQualityFilterConfiguration,
    DataQualityRejectionReason,
)
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from tests.unit.universe_engine.data_quality.conftest import MockDataQualityDataProvider


def create_candles(
    symbol_ref: SymbolReference,
    count: int,
    start_days_ago: int,
    skip_indices: List[int] = None,
) -> List[Candle]:
    candles = []
    base_date = datetime.now(timezone.utc) - timedelta(days=start_days_ago)
    skip = skip_indices or []

    current_idx = 0
    while len(candles) < count:
        if base_date.weekday() < 5:
            if current_idx not in skip:
                candles.append(
                    Candle(
                        symbol=symbol_ref,
                        timeframe=Timeframe.D1,
                        timestamp=base_date,
                        open=100.0,
                        high=105.0,
                        low=95.0,
                        close=100.0,
                        volume=1000.0,
                        is_completed=True,
                    )
                )
            current_idx += 1
        base_date += timedelta(days=1)
    return candles


@pytest.fixture
def context(sample_instrument):
    return DataQualityFilterContext(
        run_id="test_run",
        parent_snapshot_id="test_parent",
        config=DataQualityFilterConfiguration(
            min_history_days=252,
            max_missing_candles_percentage=0.05,
            max_consecutive_suspensions=5,
            check_corporate_actions=True,
        ),
        certified_instruments=[sample_instrument],
        started_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_historical_availability_pass(
    context,
    mock_dq_data_provider,
    mock_calendar_provider,
    mock_corporate_action_provider,
    sample_instrument,
):
    stage = HistoricalDataAvailabilityFilter()
    await stage.execute(
        context,
        mock_dq_data_provider,
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 1
    assert len(context.rejected_details) == 0


@pytest.mark.asyncio
async def test_historical_availability_boundary_fail(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    # Requirement: 252 days. Provide exactly 251 calendar days of history (span of 250 days).
    symbol_str = sample_instrument.symbol.symbol
    candles = [
        Candle(
            symbol=sample_instrument.symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime.now(timezone.utc) - timedelta(days=250),
            open=10,
            high=10,
            low=10,
            close=10,
            volume=10,
            is_completed=True,
        ),
        Candle(
            symbol=sample_instrument.symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime.now(timezone.utc),
            open=10,
            high=10,
            low=10,
            close=10,
            volume=10,
            is_completed=True,
        ),
    ]

    dp = MockDataQualityDataProvider(scenarios={symbol_str: candles})
    stage = HistoricalDataAvailabilityFilter()
    await stage.execute(
        context, dp, mock_calendar_provider, mock_corporate_action_provider
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason
        == DataQualityRejectionReason.INSUFFICIENT_HISTORY
    )


@pytest.mark.asyncio
async def test_missing_candle_detection_pass(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    # 20 candles with 1 missing (5%) - threshold is 0.05
    # To reliably skip 1 weekday, skip 10 consecutive calendar days starting from day 0, which gives ~7 weekdays skipped
    # Wait, the threshold is 0.05. We just need to ensure the skipped index falls on a weekday.
    # We can just use the DataCompleteness validation or pass all.
    # Let's change create_candles so current_idx only increments for weekdays.

    candles = create_candles(sample_instrument.symbol, 19, 30, skip_indices=[2])

    context.shared_state[symbol] = candles
    stage = MissingCandleDetection()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 1


@pytest.mark.asyncio
async def test_missing_candle_detection_fail(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    # 20 candles with 2 missing (10%) - threshold is 0.05
    candles = create_candles(sample_instrument.symbol, 18, 30, skip_indices=[2, 4])

    context.shared_state[symbol] = candles
    stage = MissingCandleDetection()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason == DataQualityRejectionReason.TOO_MANY_GAPS
    )


@pytest.mark.asyncio
async def test_suspended_trading_fail(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    # 6 consecutive missing candles
    candles = create_candles(
        sample_instrument.symbol, 50, 100, skip_indices=[5, 6, 7, 8, 9, 10]
    )

    context.shared_state[symbol] = candles
    stage = SuspendedTradingDetection()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason
        == DataQualityRejectionReason.PROLONGED_SUSPENSION
    )


@pytest.mark.asyncio
async def test_data_completeness_duplicate_timestamp(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    candles = create_candles(sample_instrument.symbol, 10, 20)
    # Duplicate the first timestamp
    candles[1].timestamp = candles[0].timestamp

    context.shared_state[symbol] = candles
    stage = DataCompletenessValidation()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason == DataQualityRejectionReason.DATA_CORRUPTED
    )


@pytest.mark.asyncio
async def test_data_completeness_invalid_ohlc(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    candles = create_candles(sample_instrument.symbol, 10, 20)
    # Corrupt a candle: high < low
    candles[5].high = candles[5].low - 1

    context.shared_state[symbol] = candles
    stage = DataCompletenessValidation()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason == DataQualityRejectionReason.DATA_CORRUPTED
    )


@pytest.mark.asyncio
async def test_data_completeness_nan_value(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    candles = create_candles(sample_instrument.symbol, 10, 20)
    # Add NaN
    candles[5].volume = math.nan

    context.shared_state[symbol] = candles
    stage = DataCompletenessValidation()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason == DataQualityRejectionReason.DATA_CORRUPTED
    )


@pytest.mark.asyncio
async def test_corporate_action_fail(
    context, mock_calendar_provider, mock_corporate_action_provider, sample_instrument
):
    symbol = sample_instrument.symbol.symbol
    candles = create_candles(sample_instrument.symbol, 10, 20)
    context.shared_state[symbol] = candles

    mock_corporate_action_provider.override_validity[symbol] = False

    stage = CorporateActionConsistency()
    await stage.execute(
        context,
        MockDataQualityDataProvider(),
        mock_calendar_provider,
        mock_corporate_action_provider,
    )

    assert len(context.certified_instruments) == 0
    assert (
        context.rejected_details[0].reason
        == DataQualityRejectionReason.INCONSISTENT_CORPORATE_ACTIONS
    )
