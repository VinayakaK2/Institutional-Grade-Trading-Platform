import pytest
from datetime import datetime, timezone
from backend.universe_engine.classification.models import (
    UniverseClassificationContext,
    UniverseClassificationConfiguration,
    ClassifiedSymbol,
    MarketCapClassification,
    LiquidityClassification,
    DataQualityClassification,
)
from backend.universe_engine.classification.stages import (
    SectorClassificationStage,
    IndustryClassificationStage,
    MarketCapClassificationStage,
    LiquidityClassificationStage,
    DataQualityClassificationStage,
)

@pytest.fixture
def base_context(sample_instrument_1):
    symbols = {
        "AAPL": ClassifiedSymbol(symbol=sample_instrument_1)
    }
    return UniverseClassificationContext(
        run_id="test",
        parent_certified_universe_id="cert_test",
        config=UniverseClassificationConfiguration(
            large_cap_threshold=10_000,
            mid_cap_threshold=2_000,
            high_liquidity_volume_threshold=5_000,
            medium_liquidity_volume_threshold=1_000
        ),
        classified_symbols=symbols,
        parent_liquidity_metrics={
            "AAPL": {"average_daily_volume": 6_000.0}
        },
        started_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_sector_classification_success(base_context, mock_classification_provider):
    mock_classification_provider.sectors["AAPL"] = "Technology"
    stage = SectorClassificationStage()
    await stage.execute(base_context, mock_classification_provider)
    
    assert base_context.classified_symbols["AAPL"].sector == "Technology"
    assert base_context.statistics.unknown_sector_count == 0
    assert base_context.statistics.sector_distribution["Technology"] == 1

@pytest.mark.asyncio
async def test_sector_classification_unknown_and_error(base_context, mock_classification_provider):
    # Not setting sector for AAPL
    stage = SectorClassificationStage()
    await stage.execute(base_context, mock_classification_provider)
    
    assert base_context.classified_symbols["AAPL"].sector == "UNKNOWN"
    assert base_context.statistics.unknown_sector_count == 1
    assert base_context.statistics.sector_distribution["UNKNOWN"] == 1

    # Test error
    mock_classification_provider.should_fail = True
    base_context.statistics.unknown_sector_count = 0
    await stage.execute(base_context, mock_classification_provider)
    
    assert base_context.classified_symbols["AAPL"].sector == "UNKNOWN"
    assert base_context.statistics.unknown_sector_count == 1

@pytest.mark.asyncio
async def test_industry_classification_success(base_context, mock_classification_provider):
    mock_classification_provider.industries["AAPL"] = "Consumer Electronics"
    stage = IndustryClassificationStage()
    await stage.execute(base_context, mock_classification_provider)
    
    assert base_context.classified_symbols["AAPL"].industry == "Consumer Electronics"
    assert base_context.statistics.unknown_industry_count == 0

@pytest.mark.asyncio
async def test_industry_classification_unknown_and_error(base_context, mock_classification_provider):
    stage = IndustryClassificationStage()
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].industry == "UNKNOWN"
    assert base_context.statistics.unknown_industry_count == 1

@pytest.mark.asyncio
async def test_market_cap_classification(base_context, mock_classification_provider):
    stage = MarketCapClassificationStage()
    
    # Large
    mock_classification_provider.market_caps["AAPL"] = 15_000.0
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].market_cap == MarketCapClassification.LARGE

    # Mid
    mock_classification_provider.market_caps["AAPL"] = 5_000.0
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].market_cap == MarketCapClassification.MID
    
    # Small
    mock_classification_provider.market_caps["AAPL"] = 1_000.0
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].market_cap == MarketCapClassification.SMALL
    
    # Unknown
    mock_classification_provider.market_caps["AAPL"] = None
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].market_cap == MarketCapClassification.UNKNOWN

    # Error
    mock_classification_provider.should_fail = True
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].market_cap == MarketCapClassification.UNKNOWN

@pytest.mark.asyncio
async def test_liquidity_classification(base_context, mock_classification_provider):
    stage = LiquidityClassificationStage()
    
    # High (6000)
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].liquidity == LiquidityClassification.HIGH
    
    # Medium
    base_context.parent_liquidity_metrics["AAPL"] = {"average_daily_volume": 2_000.0}
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].liquidity == LiquidityClassification.MEDIUM
    
    # Low
    base_context.parent_liquidity_metrics["AAPL"] = {"average_daily_volume": 500.0}
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].liquidity == LiquidityClassification.LOW
    
    # Unknown (Missing)
    base_context.parent_liquidity_metrics.pop("AAPL")
    await stage.execute(base_context, mock_classification_provider)
    assert base_context.classified_symbols["AAPL"].liquidity == LiquidityClassification.UNKNOWN

@pytest.mark.asyncio
async def test_data_quality_classification(base_context, mock_classification_provider):
    stage = DataQualityClassificationStage()
    await stage.execute(base_context, mock_classification_provider)
    
    assert base_context.classified_symbols["AAPL"].data_quality == DataQualityClassification.CERTIFIED
    assert base_context.statistics.data_quality_distribution[DataQualityClassification.CERTIFIED] == 1
