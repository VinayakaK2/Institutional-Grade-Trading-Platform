import pytest
from datetime import datetime, timezone

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.trend_engine.models.models import (
    TrendSymbol, TrendDirection, TrendState
)
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.providers.memory import InMemoryIndicatorProvider, InMemoryStructureProvider
from backend.trend_engine.pipeline.stages.ema_detection import EmaStructureDetectionStage
from backend.trend_engine.pipeline.stages.structure_detection import PriceStructureDetectionStage
from backend.trend_engine.pipeline.stages.trend_resolution import TrendResolutionStage
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.market_structure_engine.models.structure import MarketStructurePoint, StructureType
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType

# --- Fixtures ---

@pytest.fixture
def sample_watchlist_symbol():
    return WatchlistSymbol(
        symbol=SymbolReference(
            symbol="AAPL",
            exchange=ExchangeReference(code="NASDAQ", name="NASDAQ", country="US")
        ),
        market_segment="US_EQUITY",
        instrument_type="COMMON_STOCK",
        provider_metadata={}
    )

@pytest.fixture
def sample_trend_symbols(sample_watchlist_symbol):
    return [TrendSymbol(watchlist_symbol=sample_watchlist_symbol)]

@pytest.fixture
def context(sample_trend_symbols):
    return TrendExecutionContext(
        run_id="run_1",
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        started_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        configuration_hash="hash",
        pipeline_version="1.0.0",
        schema_version="1.0.0"
    )

def create_ema_results(ema20: float, ema50: float, ema200: float, sym: SymbolReference):
    return {
        20: IndicatorResult(symbol=sym, timeframe="1d", dataset_version="1", timestamp=datetime.now(timezone.utc), indicator_type=IndicatorType.EMA, value=ema20, parameters={"period": 20}),
        50: IndicatorResult(symbol=sym, timeframe="1d", dataset_version="1", timestamp=datetime.now(timezone.utc), indicator_type=IndicatorType.EMA, value=ema50, parameters={"period": 50}),
        200: IndicatorResult(symbol=sym, timeframe="1d", dataset_version="1", timestamp=datetime.now(timezone.utc), indicator_type=IndicatorType.EMA, value=ema200, parameters={"period": 200}),
    }

def create_structure_results(t1: StructureType, t2: StructureType):
    sp1 = SwingPoint(type=SwingType.HIGH, price=100.0, timestamp=datetime.now(timezone.utc), candle_high=100.0, candle_low=90.0, candle_open=95.0, candle_close=95.0)
    sp2 = SwingPoint(type=SwingType.LOW, price=90.0, timestamp=datetime.now(timezone.utc), candle_high=100.0, candle_low=90.0, candle_open=95.0, candle_close=95.0)
    return [
        MarketStructurePoint(
            id="1",
            type=t1,
            swing_point=sp1
        ),
        MarketStructurePoint(
            id="2",
            type=t2,
            swing_point=sp2
        )
    ]

# --- Tests ---

@pytest.mark.asyncio
async def test_bullish_uptrend(context, sample_watchlist_symbol):
    sym_key = f"{sample_watchlist_symbol.symbol.symbol}:{sample_watchlist_symbol.symbol.exchange.code}"
    
    # EMAs: 20 > 50 > 200
    ind_provider = InMemoryIndicatorProvider({sym_key: create_ema_results(150, 100, 50, sample_watchlist_symbol.symbol)})
    # Structure: HH, HL
    str_provider = InMemoryStructureProvider({sym_key: create_structure_results(StructureType.HH, StructureType.HL)})
    
    ema_stage = EmaStructureDetectionStage(ind_provider)
    str_stage = PriceStructureDetectionStage(str_provider)
    res_stage = TrendResolutionStage()
    
    await ema_stage.execute(context)
    await str_stage.execute(context)
    await res_stage.execute(context)
    
    ts = context.symbols[0]
    assert ts.stage_metadata["ema_alignment"] == "BULLISH"
    assert ts.stage_metadata["structure_alignment"] == "BULLISH"
    assert ts.direction == TrendDirection.UPTREND
    assert ts.state == TrendState.VALID

@pytest.mark.asyncio
async def test_bearish_downtrend(context, sample_watchlist_symbol):
    sym_key = f"{sample_watchlist_symbol.symbol.symbol}:{sample_watchlist_symbol.symbol.exchange.code}"
    
    # EMAs: 20 < 50 < 200
    ind_provider = InMemoryIndicatorProvider({sym_key: create_ema_results(50, 100, 150, sample_watchlist_symbol.symbol)})
    # Structure: LH, LL
    str_provider = InMemoryStructureProvider({sym_key: create_structure_results(StructureType.LH, StructureType.LL)})
    
    ema_stage = EmaStructureDetectionStage(ind_provider)
    str_stage = PriceStructureDetectionStage(str_provider)
    res_stage = TrendResolutionStage()
    
    await ema_stage.execute(context)
    await str_stage.execute(context)
    await res_stage.execute(context)
    
    ts = context.symbols[0]
    assert ts.stage_metadata["ema_alignment"] == "BEARISH"
    assert ts.stage_metadata["structure_alignment"] == "BEARISH"
    assert ts.direction == TrendDirection.DOWNTREND
    assert ts.state == TrendState.VALID

@pytest.mark.asyncio
async def test_sideways_mixed(context, sample_watchlist_symbol):
    sym_key = f"{sample_watchlist_symbol.symbol.symbol}:{sample_watchlist_symbol.symbol.exchange.code}"
    
    # EMAs: 20 > 50 > 200 (BULLISH)
    ind_provider = InMemoryIndicatorProvider({sym_key: create_ema_results(150, 100, 50, sample_watchlist_symbol.symbol)})
    # Structure: LH, LL (BEARISH) - they disagree
    str_provider = InMemoryStructureProvider({sym_key: create_structure_results(StructureType.LH, StructureType.LL)})
    
    ema_stage = EmaStructureDetectionStage(ind_provider)
    str_stage = PriceStructureDetectionStage(str_provider)
    res_stage = TrendResolutionStage()
    
    await ema_stage.execute(context)
    await str_stage.execute(context)
    await res_stage.execute(context)
    
    ts = context.symbols[0]
    assert ts.stage_metadata["ema_alignment"] == "BULLISH"
    assert ts.stage_metadata["structure_alignment"] == "BEARISH"
    assert ts.direction == TrendDirection.SIDEWAYS
    assert ts.state == TrendState.INVALID

@pytest.mark.asyncio
async def test_missing_data_unknown(context, sample_watchlist_symbol):
    
    # Empty providers -> missing data
    ind_provider = InMemoryIndicatorProvider({})
    str_provider = InMemoryStructureProvider({})
    
    ema_stage = EmaStructureDetectionStage(ind_provider)
    str_stage = PriceStructureDetectionStage(str_provider)
    res_stage = TrendResolutionStage()
    
    await ema_stage.execute(context)
    await str_stage.execute(context)
    await res_stage.execute(context)
    
    ts = context.symbols[0]
    assert ts.stage_metadata["ema_alignment"] == "UNKNOWN"
    assert ts.stage_metadata["structure_alignment"] == "UNKNOWN"
    assert ts.direction == TrendDirection.UNKNOWN
    assert ts.state == TrendState.INCOMPLETE

@pytest.mark.asyncio
async def test_invalid_ema_sideways(context, sample_watchlist_symbol):
    sym_key = f"{sample_watchlist_symbol.symbol.symbol}:{sample_watchlist_symbol.symbol.exchange.code}"
    
    # EMAs: 20 > 50 but 50 < 200 (INVALID)
    ind_provider = InMemoryIndicatorProvider({sym_key: create_ema_results(150, 100, 200, sample_watchlist_symbol.symbol)})
    # Structure: HH, HL (BULLISH)
    str_provider = InMemoryStructureProvider({sym_key: create_structure_results(StructureType.HH, StructureType.HL)})
    
    ema_stage = EmaStructureDetectionStage(ind_provider)
    str_stage = PriceStructureDetectionStage(str_provider)
    res_stage = TrendResolutionStage()
    
    await ema_stage.execute(context)
    await str_stage.execute(context)
    await res_stage.execute(context)
    
    ts = context.symbols[0]
    assert ts.stage_metadata["ema_alignment"] == "INVALID"
    assert ts.stage_metadata["structure_alignment"] == "BULLISH"
    assert ts.direction == TrendDirection.SIDEWAYS
    assert ts.state == TrendState.INVALID
