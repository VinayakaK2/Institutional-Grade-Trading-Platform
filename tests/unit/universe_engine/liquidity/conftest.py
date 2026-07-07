import pytest
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from backend.universe_engine.contracts.liquidity import ILiquidityDataProvider, IFundamentalDataProvider
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment

class MockLiquidityDataProvider(ILiquidityDataProvider):
    """
    Deterministic provider for testing based on instrument ticker.
    """
    async def get_historical_candles(self, instrument: UniverseInstrument, lookback_days: int) -> List[Candle]:
        symbol = instrument.symbol.symbol
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        
        # Determine values based on symbol name (deterministic)
        if "FAIL_VOL" in symbol:
            vol, close = 100_000.0, 10.0
        elif "FAIL_TURN" in symbol:
            # e.g., config requires 1_000_000 turnover, 500,000 volume
            vol, close = 500_000.0, 1.5  # Vol: 500,000 (PASS), Turnover = 750,000 (FAIL)
        elif "FAIL_PRICE" in symbol:
            vol, close = 1_000_000.0, 1.5  # Vol: 1,000,000 (PASS), Turnover: 1,500,000 (PASS), Price: 1.5 (FAIL)
        elif "MISSING_CANDLES" in symbol:
            return []
        elif "BOUNDARY_VOL" in symbol:
            vol, close = 500_000.0, 10.0 # exact boundary
        else:
            # PASS
            vol, close = 1_000_000.0, 10.0 # Turnover 10M
            
        candles = []
        for i in range(lookback_days):
            candles.append(Candle(
                symbol=instrument.symbol,
                timeframe=Timeframe.D1,
                timestamp=base_time - timedelta(days=lookback_days - i),
                open=close,
                high=close + 0.5,
                low=close - 0.5,
                close=close,
                volume=vol
            ))
        return candles

class MockFundamentalDataProvider(IFundamentalDataProvider):
    """
    Deterministic provider for testing based on instrument ticker.
    """
    async def get_market_capitalization(self, instrument: UniverseInstrument) -> Optional[float]:
        symbol = instrument.symbol.symbol
        
        if "FAIL_MCAP" in symbol:
            return 10_000_000.0 # threshold is 50M
        elif "MISSING_MCAP" in symbol:
            return None
        elif "BOUNDARY_MCAP" in symbol:
            return 50_000_000.0
        else:
            return 100_000_000.0 # Pass

@pytest.fixture
def mock_data_provider():
    return MockLiquidityDataProvider()

@pytest.fixture
def mock_fundamental_provider():
    return MockFundamentalDataProvider()

@pytest.fixture
def create_test_instrument():
    def _create(symbol: str) -> UniverseInstrument:
        return UniverseInstrument(
            symbol=SymbolReference(symbol=symbol, exchange=ExchangeReference(code="NSE")),
            instrument_type=InstrumentType.EQUITY,
            trading_status=TradingStatus.ACTIVE,
            market_segment=MarketSegment.EQUITY_CASH,
            is_delisted=False
        )
    return _create
