from backend.universe_engine.contracts.classification import IClassificationStage, IClassificationDataProvider
from backend.universe_engine.classification.models import (
    UniverseClassificationContext,
    MarketCapClassification,
    LiquidityClassification,
    DataQualityClassification,
)
from backend.core.logger import get_logger

logger = get_logger(__name__)

class SectorClassificationStage(IClassificationStage):
    @property
    def name(self) -> str:
        return "SectorClassificationStage"

    async def execute(self, context: UniverseClassificationContext, provider: IClassificationDataProvider) -> None:
        for symbol_str, classified in context.classified_symbols.items():
            try:
                sector = await provider.get_sector(classified.symbol)
                if sector:
                    classified.sector = sector
                else:
                    classified.sector = "UNKNOWN"
                    context.statistics.unknown_sector_count += 1
            except Exception as e:
                logger.warning(f"Failed to fetch sector for {symbol_str}: {str(e)}")
                classified.sector = "UNKNOWN"
                context.statistics.unknown_sector_count += 1
            
            context.statistics.sector_distribution[classified.sector] = \
                context.statistics.sector_distribution.get(classified.sector, 0) + 1


class IndustryClassificationStage(IClassificationStage):
    @property
    def name(self) -> str:
        return "IndustryClassificationStage"

    async def execute(self, context: UniverseClassificationContext, provider: IClassificationDataProvider) -> None:
        for symbol_str, classified in context.classified_symbols.items():
            try:
                industry = await provider.get_industry(classified.symbol)
                if industry:
                    classified.industry = industry
                else:
                    classified.industry = "UNKNOWN"
                    context.statistics.unknown_industry_count += 1
            except Exception as e:
                logger.warning(f"Failed to fetch industry for {symbol_str}: {str(e)}")
                classified.industry = "UNKNOWN"
                context.statistics.unknown_industry_count += 1
                
            context.statistics.industry_distribution[classified.industry] = \
                context.statistics.industry_distribution.get(classified.industry, 0) + 1


class MarketCapClassificationStage(IClassificationStage):
    @property
    def name(self) -> str:
        return "MarketCapClassificationStage"

    async def execute(self, context: UniverseClassificationContext, provider: IClassificationDataProvider) -> None:
        for symbol_str, classified in context.classified_symbols.items():
            try:
                mcap = await provider.get_market_cap(classified.symbol)
                if mcap is None:
                    classified.market_cap = MarketCapClassification.UNKNOWN
                elif mcap >= context.config.large_cap_threshold:
                    classified.market_cap = MarketCapClassification.LARGE
                elif mcap >= context.config.mid_cap_threshold:
                    classified.market_cap = MarketCapClassification.MID
                else:
                    classified.market_cap = MarketCapClassification.SMALL
            except Exception as e:
                logger.warning(f"Failed to fetch market cap for {symbol_str}: {str(e)}")
                classified.market_cap = MarketCapClassification.UNKNOWN

            cat = classified.market_cap.value
            context.statistics.market_cap_distribution[cat] = \
                context.statistics.market_cap_distribution.get(cat, 0) + 1


class LiquidityClassificationStage(IClassificationStage):
    @property
    def name(self) -> str:
        return "LiquidityClassificationStage"

    async def execute(self, context: UniverseClassificationContext, provider: IClassificationDataProvider) -> None:
        # Note: We do not use the provider here; we use context.parent_liquidity_metrics.
        for symbol_str, classified in context.classified_symbols.items():
            metrics = context.parent_liquidity_metrics.get(symbol_str, {})
            adv = metrics.get("average_daily_volume")
            
            if adv is None:
                classified.liquidity = LiquidityClassification.UNKNOWN
            elif adv >= context.config.high_liquidity_volume_threshold:
                classified.liquidity = LiquidityClassification.HIGH
            elif adv >= context.config.medium_liquidity_volume_threshold:
                classified.liquidity = LiquidityClassification.MEDIUM
            else:
                classified.liquidity = LiquidityClassification.LOW
                
            cat = classified.liquidity.value
            context.statistics.liquidity_distribution[cat] = \
                context.statistics.liquidity_distribution.get(cat, 0) + 1


class DataQualityClassificationStage(IClassificationStage):
    @property
    def name(self) -> str:
        return "DataQualityClassificationStage"

    async def execute(self, context: UniverseClassificationContext, provider: IClassificationDataProvider) -> None:
        # Since Phase 5.5 only processes the certified subset of symbols (as passed from Phase 5.4 output),
        # all instruments in the context are implicitly CERTIFIED.
        for symbol_str, classified in context.classified_symbols.items():
            classified.data_quality = DataQualityClassification.CERTIFIED
            
            cat = classified.data_quality.value
            context.statistics.data_quality_distribution[cat] = \
                context.statistics.data_quality_distribution.get(cat, 0) + 1
