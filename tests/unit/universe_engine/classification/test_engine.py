import pytest
from backend.universe_engine.classification.models import (
    MarketCapClassification,
    LiquidityClassification,
    DataQualityClassification,
)

@pytest.mark.asyncio
async def test_generate_classified_universe(test_engine, mock_classification_provider, parent_certified_universe, parent_liquidity_metrics):
    mock_classification_provider.sectors["AAPL"] = "Technology"
    mock_classification_provider.industries["AAPL"] = "Consumer Electronics"
    mock_classification_provider.market_caps["AAPL"] = 3_000_000_000_000.0 # Large

    mock_classification_provider.sectors["MSFT"] = "Technology"
    mock_classification_provider.industries["MSFT"] = "Software"
    mock_classification_provider.market_caps["MSFT"] = 2_000_000_000.0 # Mid

    result = await test_engine.generate_classified_universe(
        run_id="test_run",
        parent_certified_universe=parent_certified_universe,
        parent_liquidity_metrics=parent_liquidity_metrics
    )

    universe = result.universe
    assert universe.parent_certified_universe_id == parent_certified_universe.certified_universe_id
    assert len(universe.classified_symbols) == 2
    assert universe.statistics.total_symbols == 2
    assert universe.pipeline_version == "1.0.0"

    aapl = next(s for s in universe.classified_symbols if s.symbol.symbol.symbol == "AAPL")
    msft = next(s for s in universe.classified_symbols if s.symbol.symbol.symbol == "MSFT")

    assert aapl.sector == "Technology"
    assert aapl.industry == "Consumer Electronics"
    assert aapl.market_cap == MarketCapClassification.LARGE
    assert aapl.liquidity == LiquidityClassification.HIGH
    assert aapl.data_quality == DataQualityClassification.CERTIFIED

    assert msft.sector == "Technology"
    assert msft.industry == "Software"
    assert msft.market_cap == MarketCapClassification.MID
    assert msft.liquidity == LiquidityClassification.LOW # parent metrics: 500k < 1m
    assert msft.data_quality == DataQualityClassification.CERTIFIED

    # Check that it's persisted in the repo
    loaded = await test_engine._repository.load_classified_universe(universe.classified_universe_id)
    assert loaded is not None
    assert loaded.classified_universe_id == universe.classified_universe_id


@pytest.mark.asyncio
async def test_classification_determinism(test_engine, mock_classification_provider, parent_certified_universe, parent_liquidity_metrics):
    mock_classification_provider.sectors['AAPL'] = 'Technology'
    mock_classification_provider.industries['AAPL'] = 'Consumer Electronics'
    mock_classification_provider.market_caps['AAPL'] = 3_000_000_000_000.0 

    mock_classification_provider.sectors['MSFT'] = 'Technology'
    mock_classification_provider.industries['MSFT'] = 'Software'
    mock_classification_provider.market_caps['MSFT'] = 2_000_000_000.0 

    result_1 = await test_engine.generate_classified_universe(
        run_id='run_1',
        parent_certified_universe=parent_certified_universe,
        parent_liquidity_metrics=parent_liquidity_metrics
    )

    result_2 = await test_engine.generate_classified_universe(
        run_id='run_2',
        parent_certified_universe=parent_certified_universe,
        parent_liquidity_metrics=parent_liquidity_metrics
    )

    u1 = result_1.universe
    u2 = result_2.universe

    assert u1.parent_certified_universe_id == u2.parent_certified_universe_id
    assert u1.pipeline_version == u2.pipeline_version
    assert u1.config_hash == u2.config_hash
    
    assert len(u1.classified_symbols) == len(u2.classified_symbols)
    for s1, s2 in zip(u1.classified_symbols, u2.classified_symbols):
        assert s1.symbol.symbol.symbol == s2.symbol.symbol.symbol
        assert s1.sector == s2.sector
        assert s1.industry == s2.industry
        assert s1.market_cap == s2.market_cap
        assert s1.liquidity == s2.liquidity
        assert s1.data_quality == s2.data_quality

