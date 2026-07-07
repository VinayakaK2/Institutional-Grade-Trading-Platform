from backend.universe_engine.contracts.liquidity import (
    ILiquidityStage,
    ILiquidityDataProvider,
    IFundamentalDataProvider
)
from backend.universe_engine.liquidity.models import (
    LiquidityFilterContext,
    RejectionDetail,
    LiquidityRejectionReason
)
from backend.core.logger import get_logger
from backend.universe_engine.liquidity.exceptions import MissingLiquidityDataError

logger = get_logger(__name__)

class AverageDailyVolumeFilter(ILiquidityStage):
    @property
    def name(self) -> str:
        return "AverageDailyVolumeFilter"

    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider, 
        fundamental_provider: IFundamentalDataProvider
    ) -> None:
        lookback = context.config.volume_lookback_days
        threshold = context.config.min_average_daily_volume
        
        retained = []
        for instrument in context.qualified_instruments:
            try:
                candles = await data_provider.get_historical_candles(instrument, lookback)
                if not candles:
                    raise MissingLiquidityDataError("No candles returned")
                
                avg_volume = sum(c.volume for c in candles) / len(candles)
                
                if avg_volume >= threshold:
                    context.liquidity_metrics.setdefault(instrument.symbol.symbol, {})["average_daily_volume"] = avg_volume
                    retained.append(instrument)
                else:
                    context.rejected_details.append(RejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=LiquidityRejectionReason.VOLUME_BELOW_THRESHOLD,
                        measured_value=f"{avg_volume:.2f}",
                        threshold=str(threshold)
                    ))
                    context.statistics.volume_rejections += 1
            except MissingLiquidityDataError:
                context.rejected_details.append(RejectionDetail(
                    instrument_symbol=instrument.symbol.symbol,
                    stage_name=self.name,
                    reason=LiquidityRejectionReason.MISSING_DATA,
                    measured_value="None",
                    threshold=str(threshold)
                ))
                context.statistics.missing_data_rejections += 1
                
        context.qualified_instruments = retained


class AverageDailyTurnoverFilter(ILiquidityStage):
    @property
    def name(self) -> str:
        return "AverageDailyTurnoverFilter"

    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider, 
        fundamental_provider: IFundamentalDataProvider
    ) -> None:
        lookback = context.config.turnover_lookback_days
        threshold = context.config.min_average_daily_turnover
        
        retained = []
        for instrument in context.qualified_instruments:
            try:
                candles = await data_provider.get_historical_candles(instrument, lookback)
                if not candles:
                    raise MissingLiquidityDataError("No candles returned")
                
                avg_turnover = sum(c.volume * c.close for c in candles) / len(candles)
                
                if avg_turnover >= threshold:
                    context.liquidity_metrics.setdefault(instrument.symbol.symbol, {})["average_daily_turnover"] = avg_turnover
                    retained.append(instrument)
                else:
                    context.rejected_details.append(RejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=LiquidityRejectionReason.TURNOVER_BELOW_THRESHOLD,
                        measured_value=f"{avg_turnover:.2f}",
                        threshold=str(threshold)
                    ))
                    context.statistics.turnover_rejections += 1
            except MissingLiquidityDataError:
                context.rejected_details.append(RejectionDetail(
                    instrument_symbol=instrument.symbol.symbol,
                    stage_name=self.name,
                    reason=LiquidityRejectionReason.MISSING_DATA,
                    measured_value="None",
                    threshold=str(threshold)
                ))
                context.statistics.missing_data_rejections += 1
                
        context.qualified_instruments = retained


class MinimumPriceFilter(ILiquidityStage):
    @property
    def name(self) -> str:
        return "MinimumPriceFilter"

    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider, 
        fundamental_provider: IFundamentalDataProvider
    ) -> None:
        lookback = context.config.price_lookback_days
        threshold = context.config.min_close_price
        
        retained = []
        for instrument in context.qualified_instruments:
            try:
                candles = await data_provider.get_historical_candles(instrument, lookback)
                if not candles:
                    raise MissingLiquidityDataError("No candles returned")
                
                # Check the most recent close price
                latest_close = candles[-1].close
                
                if latest_close >= threshold:
                    retained.append(instrument)
                else:
                    context.rejected_details.append(RejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=LiquidityRejectionReason.PRICE_BELOW_THRESHOLD,
                        measured_value=f"{latest_close:.2f}",
                        threshold=str(threshold)
                    ))
                    context.statistics.price_rejections += 1
            except MissingLiquidityDataError:
                context.rejected_details.append(RejectionDetail(
                    instrument_symbol=instrument.symbol.symbol,
                    stage_name=self.name,
                    reason=LiquidityRejectionReason.MISSING_DATA,
                    measured_value="None",
                    threshold=str(threshold)
                ))
                context.statistics.missing_data_rejections += 1
                
        context.qualified_instruments = retained


class MinimumMarketCapFilter(ILiquidityStage):
    @property
    def name(self) -> str:
        return "MinimumMarketCapFilter"

    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider, 
        fundamental_provider: IFundamentalDataProvider
    ) -> None:
        threshold = context.config.min_market_capitalization
        
        retained = []
        for instrument in context.qualified_instruments:
            try:
                mcap = await fundamental_provider.get_market_capitalization(instrument)
                if mcap is None:
                    raise MissingLiquidityDataError("Market cap not available")
                
                if mcap >= threshold:
                    context.liquidity_metrics.setdefault(instrument.symbol.symbol, {})["market_cap"] = mcap
                    retained.append(instrument)
                else:
                    context.rejected_details.append(RejectionDetail(
                        instrument_symbol=instrument.symbol.symbol,
                        stage_name=self.name,
                        reason=LiquidityRejectionReason.MARKET_CAP_BELOW_THRESHOLD,
                        measured_value=f"{mcap:.2f}",
                        threshold=str(threshold)
                    ))
                    context.statistics.market_cap_rejections += 1
            except MissingLiquidityDataError:
                context.rejected_details.append(RejectionDetail(
                    instrument_symbol=instrument.symbol.symbol,
                    stage_name=self.name,
                    reason=LiquidityRejectionReason.MISSING_DATA,
                    measured_value="None",
                    threshold=str(threshold)
                ))
                context.statistics.missing_data_rejections += 1
                
        context.qualified_instruments = retained
