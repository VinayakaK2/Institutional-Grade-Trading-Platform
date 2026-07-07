import pytest
from backend.universe_engine.stages.filters import (
    ExchangeFilterStage,
    MarketSegmentFilterStage,
    InstrumentTypeFilterStage,
    TradingStatusFilterStage,
    DelistedFilterStage,
)
from backend.universe_engine.models.universe import (
    UniverseExecutionContext,
    UniverseInstrument,
    InstrumentType,
    TradingStatus,
    MarketSegment,
)
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from datetime import datetime, timezone

@pytest.fixture
def base_context():
    return UniverseExecutionContext(
        run_id="test-run",
        snapshot_id="test-snap",
        provider_name="test-provider",
        started_at=datetime.now(timezone.utc),
        instruments=[],
        shared_state={},
        metadata={},
        stage_results=[],
    )

def create_instrument(exchange="NSE", segment=MarketSegment.EQUITY_CASH, 
                      inst_type=InstrumentType.EQUITY, status=TradingStatus.ACTIVE, 
                      delisted=False) -> UniverseInstrument:
    return UniverseInstrument(
        symbol=SymbolReference(symbol="TEST", exchange=ExchangeReference(code=exchange)),
        instrument_type=inst_type,
        trading_status=status,
        market_segment=segment,
        is_delisted=delisted,
        provider_attributes={}
    )

@pytest.mark.asyncio
async def test_exchange_filter_stage(base_context):
    base_context.instruments = [
        create_instrument(exchange="NSE"),
        create_instrument(exchange="BSE"),
        create_instrument(exchange="NYSE"),
    ]
    
    stage = ExchangeFilterStage(allowed_exchanges=["NSE", "BSE"])
    result = await stage.execute(base_context)
    
    assert result.status == "SUCCESS"
    assert len(base_context.instruments) == 2
    assert base_context.instruments[0].symbol.exchange.code == "NSE"
    assert base_context.instruments[1].symbol.exchange.code == "BSE"

@pytest.mark.asyncio
async def test_market_segment_filter_stage(base_context):
    base_context.instruments = [
        create_instrument(segment=MarketSegment.EQUITY_CASH),
        create_instrument(segment=MarketSegment.EQUITY_DERIVATIVES),
    ]
    
    stage = MarketSegmentFilterStage(allowed_segments=["EQUITY_CASH"])
    await stage.execute(base_context)
    
    assert len(base_context.instruments) == 1
    assert base_context.instruments[0].market_segment == MarketSegment.EQUITY_CASH

@pytest.mark.asyncio
async def test_instrument_type_filter_stage(base_context):
    base_context.instruments = [
        create_instrument(inst_type=InstrumentType.EQUITY),
        create_instrument(inst_type=InstrumentType.ETF),
        create_instrument(inst_type=InstrumentType.FUTURES),
    ]
    
    stage = InstrumentTypeFilterStage(allowed_types=["EQUITY", "ETF"])
    await stage.execute(base_context)
    
    assert len(base_context.instruments) == 2
    assert base_context.instruments[0].instrument_type == InstrumentType.EQUITY
    assert base_context.instruments[1].instrument_type == InstrumentType.ETF

@pytest.mark.asyncio
async def test_trading_status_filter_stage(base_context):
    base_context.instruments = [
        create_instrument(status=TradingStatus.ACTIVE),
        create_instrument(status=TradingStatus.SUSPENDED),
        create_instrument(status=TradingStatus.HALTED),
    ]
    
    stage = TradingStatusFilterStage(rejected_statuses=["SUSPENDED", "HALTED", "DISABLED", "INACTIVE", "UNKNOWN"])
    await stage.execute(base_context)
    
    assert len(base_context.instruments) == 1
    assert base_context.instruments[0].trading_status == TradingStatus.ACTIVE

@pytest.mark.asyncio
async def test_delisted_filter_stage(base_context):
    base_context.instruments = [
        create_instrument(delisted=False),
        create_instrument(delisted=True),
    ]
    
    stage = DelistedFilterStage(remove_delisted=True)
    await stage.execute(base_context)
    
    assert len(base_context.instruments) == 1
    assert base_context.instruments[0].is_delisted is False

@pytest.mark.asyncio
async def test_delisted_filter_stage_disabled(base_context):
    base_context.instruments = [
        create_instrument(delisted=False),
        create_instrument(delisted=True),
    ]
    
    stage = DelistedFilterStage(remove_delisted=False)
    await stage.execute(base_context)
    
    assert len(base_context.instruments) == 2
