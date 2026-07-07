import math
from typing import List
from backend.core.logger import get_logger

from backend.universe_engine.contracts.data_quality import (
    IDataQualityStage,
    IDataQualityDataProvider,
    IMarketCalendarProvider,
    ICorporateActionProvider,
)
from backend.universe_engine.data_quality.models import (
    DataQualityFilterContext,
    DataQualityRejectionReason,
    DataQualityRejectionDetail,
)
from backend.market_data.models.candle import Candle
from backend.universe_engine.data_quality.exceptions import (
    MissingDataQualityDataError,
    MissingMarketCalendarError,
)

logger = get_logger(__name__)


class HistoricalDataAvailabilityFilter(IDataQualityStage):
    @property
    def name(self) -> str:
        return "HistoricalDataAvailabilityFilter"

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> None:
        lookback = context.config.min_history_days
        surviving = []
        for instrument in context.certified_instruments:
            try:
                candles = await data_provider.get_historical_candles(
                    instrument, lookback
                )
                if not candles:
                    raise MissingDataQualityDataError("No candles returned.")

                # Check history length: Earliest candle should be at least 'lookback' days before the latest candle
                # Or simply we check the count if it's trading days, but the config says "calendar days of history"
                # Actually, typically we just check if (latest_date - earliest_date).days >= min_history_days
                earliest = min(c.timestamp for c in candles).date()
                latest = max(c.timestamp for c in candles).date()

                history_days = (latest - earliest).days
                if (
                    history_days < lookback - 1
                ):  # -1 for boundary e.g. 252 days means 251 difference
                    context.rejected_details.append(
                        DataQualityRejectionDetail(
                            instrument_symbol=instrument.symbol.symbol,
                            stage_name=self.name,
                            reason=DataQualityRejectionReason.INSUFFICIENT_HISTORY,
                            measured_value=str(history_days + 1),
                            threshold=str(lookback),
                        )
                    )
                    context.statistics.history_rejections += 1
                else:
                    surviving.append(instrument)
                    context.shared_state[instrument.symbol.symbol] = candles

            except MissingDataQualityDataError:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.MISSING_DATA,
                        measured_value="0",
                        threshold=str(lookback),
                    )
                )
                context.statistics.missing_data_rejections += 1

        context.certified_instruments = surviving


class MissingCandleDetection(IDataQualityStage):
    @property
    def name(self) -> str:
        return "MissingCandleDetection"

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> None:
        surviving = []
        max_percentage = context.config.max_missing_candles_percentage

        for instrument in context.certified_instruments:
            candles: List[Candle] = context.shared_state.get(
                instrument.symbol.symbol, []
            )
            if not candles:
                continue  # Safety fallback

            earliest = min(c.timestamp for c in candles).date()
            latest = max(c.timestamp for c in candles).date()

            expected_sessions = await calendar_provider.get_expected_trading_sessions(
                instrument, earliest, latest
            )

            if not expected_sessions:
                raise MissingMarketCalendarError(
                    f"No trading sessions found for {instrument.symbol.symbol}"
                )

            actual_dates = {c.timestamp.date() for c in candles}
            # Missing dates are those expected but not present
            missing_dates = expected_sessions - actual_dates

            missing_count = len(missing_dates)
            expected_count = len(expected_sessions)
            missing_percentage = (
                missing_count / expected_count if expected_count > 0 else 0.0
            )

            if missing_percentage > max_percentage:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.TOO_MANY_GAPS,
                        measured_value=f"{missing_percentage:.4f}",
                        threshold=f"{max_percentage:.4f}",
                    )
                )
                context.statistics.gap_rejections += 1
            else:
                surviving.append(instrument)

        context.certified_instruments = surviving


class SuspendedTradingDetection(IDataQualityStage):
    @property
    def name(self) -> str:
        return "SuspendedTradingDetection"

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> None:
        surviving = []
        max_consecutive = context.config.max_consecutive_suspensions

        for instrument in context.certified_instruments:
            candles: List[Candle] = context.shared_state.get(
                instrument.symbol.symbol, []
            )
            earliest = min(c.timestamp for c in candles).date()
            latest = max(c.timestamp for c in candles).date()

            expected_sessions = await calendar_provider.get_expected_trading_sessions(
                instrument, earliest, latest
            )

            # Sort expected sessions to iterate chronologically
            sorted_expected = sorted(list(expected_sessions))
            actual_dates = {c.timestamp.date() for c in candles}

            max_consecutive_missing = 0
            current_consecutive = 0

            for session in sorted_expected:
                if session not in actual_dates:
                    current_consecutive += 1
                    if current_consecutive > max_consecutive_missing:
                        max_consecutive_missing = current_consecutive
                else:
                    current_consecutive = 0

            if max_consecutive_missing > max_consecutive:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.PROLONGED_SUSPENSION,
                        measured_value=str(max_consecutive_missing),
                        threshold=str(max_consecutive),
                    )
                )
                context.statistics.suspension_rejections += 1
            else:
                surviving.append(instrument)

        context.certified_instruments = surviving


class DataCompletenessValidation(IDataQualityStage):
    @property
    def name(self) -> str:
        return "DataCompletenessValidation"

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> None:
        surviving = []

        for instrument in context.certified_instruments:
            candles: List[Candle] = context.shared_state.get(
                instrument.symbol.symbol, []
            )
            is_valid = True

            # Check chronological ordering and duplicates
            sorted_candles = sorted(candles, key=lambda c: c.timestamp)
            for i in range(1, len(sorted_candles)):
                if sorted_candles[i].timestamp <= sorted_candles[i - 1].timestamp:
                    is_valid = False
                    break

            if not is_valid:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.DATA_CORRUPTED,
                        measured_value="DUPLICATE_OR_UNORDERED",
                        threshold="STRICT_ORDERING",
                    )
                )
                context.statistics.completeness_rejections += 1
                continue

            # Check OHLC logic and NaNs
            for c in candles:
                if (
                    math.isnan(c.open)
                    or math.isnan(c.high)
                    or math.isnan(c.low)
                    or math.isnan(c.close)
                    or math.isnan(c.volume)
                ):
                    is_valid = False
                    break
                if c.high < c.low or c.high < c.open or c.high < c.close:
                    is_valid = False
                    break
                if c.low > c.open or c.low > c.close:
                    is_valid = False
                    break

            if not is_valid:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.DATA_CORRUPTED,
                        measured_value="INVALID_OHLC_OR_NAN",
                        threshold="VALID_OHLC",
                    )
                )
                context.statistics.completeness_rejections += 1
            else:
                surviving.append(instrument)

        context.certified_instruments = surviving


class CorporateActionConsistency(IDataQualityStage):
    @property
    def name(self) -> str:
        return "CorporateActionConsistency"

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> None:
        if not context.config.check_corporate_actions:
            return

        surviving = []

        for instrument in context.certified_instruments:
            candles: List[Candle] = context.shared_state.get(
                instrument.symbol.symbol, []
            )
            dataset_version = await data_provider.get_dataset_version(instrument)

            is_consistent = await corporate_action_provider.verify_adjustments_applied(
                instrument=instrument, candles=candles, dataset_version=dataset_version
            )

            if not is_consistent:
                context.rejected_details.append(
                    DataQualityRejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=DataQualityRejectionReason.INCONSISTENT_CORPORATE_ACTIONS,
                        measured_value="INCONSISTENT",
                        threshold="CONSISTENT",
                    )
                )
                context.statistics.corporate_action_rejections += 1
            else:
                surviving.append(instrument)

        context.certified_instruments = surviving
