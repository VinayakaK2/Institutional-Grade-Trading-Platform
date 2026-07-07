import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.universe_engine.builder.builder import MarketUniverseBuilder
from backend.universe_engine.builder.config import MarketBuilderConfig
from backend.universe_engine.contracts.engine import IUniverseEngine
from backend.universe_engine.contracts.pipeline import IUniversePipeline
from backend.universe_engine.stages.filters import (
    ExchangeFilterStage,
    MarketSegmentFilterStage,
    InstrumentTypeFilterStage,
    TradingStatusFilterStage,
    DelistedFilterStage,
)

def test_market_universe_builder_registers_stages():
    mock_engine = MagicMock(spec=IUniverseEngine)
    mock_pipeline = MagicMock(spec=IUniversePipeline)
    
    config = MarketBuilderConfig(
        allowed_exchanges=["NSE"],
        allowed_market_segments=["EQUITY_CASH"],
        allowed_instrument_types=["EQUITY"],
        rejected_trading_statuses=["SUSPENDED"],
        remove_delisted=True
    )
    
    builder = MarketUniverseBuilder(
        engine=mock_engine,
        pipeline=mock_pipeline,
        config=config
    )
    
    # Check that the pipeline register_stage was called 5 times
    assert mock_pipeline.register_stage.call_count == 5
    
    # Get the stages registered
    registered_stages = [call.args[0] for call in mock_pipeline.register_stage.call_args_list]
    
    assert isinstance(registered_stages[0], ExchangeFilterStage)
    assert isinstance(registered_stages[1], MarketSegmentFilterStage)
    assert isinstance(registered_stages[2], InstrumentTypeFilterStage)
    assert isinstance(registered_stages[3], TradingStatusFilterStage)
    assert isinstance(registered_stages[4], DelistedFilterStage)

def test_market_universe_builder_skips_empty_config():
    mock_engine = MagicMock(spec=IUniverseEngine)
    mock_pipeline = MagicMock(spec=IUniversePipeline)
    
    config = MarketBuilderConfig(
        allowed_exchanges=[],
        allowed_market_segments=[],
        allowed_instrument_types=[],
        rejected_trading_statuses=[],
        remove_delisted=False
    )
    
    builder = MarketUniverseBuilder(
        engine=mock_engine,
        pipeline=mock_pipeline,
        config=config
    )
    
    assert mock_pipeline.register_stage.call_count == 0

@pytest.mark.asyncio
async def test_market_universe_builder_build():
    mock_engine = MagicMock(spec=IUniverseEngine)
    mock_engine.generate_universe = AsyncMock(return_value="mock_result")
    mock_pipeline = MagicMock(spec=IUniversePipeline)
    
    config = MarketBuilderConfig()
    
    builder = MarketUniverseBuilder(
        engine=mock_engine,
        pipeline=mock_pipeline,
        config=config
    )
    
    result = await builder.build("run-123")
    
    assert result == "mock_result"
    mock_engine.generate_universe.assert_called_once_with("run-123")
