import pytest
from datetime import datetime, date, timedelta, timezone
from typing import List, Set

from backend.universe_engine.contracts.data_quality import (
    IDataQualityDataProvider,
    IMarketCalendarProvider,
    ICorporateActionProvider,
)
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.candle import Candle, Timeframe
from backend.universe_engine.models.universe import (
    UniverseInstrument,
    InstrumentType,
    TradingStatus,
    MarketSegment,
)
from backend.universe_engine.data_quality.exceptions import MissingDataQualityDataError


class MockDataQualityDataProvider(IDataQualityDataProvider):
    def __init__(self, scenarios: dict = None):
        self.scenarios = scenarios or {}

    async def get_historical_candles(
        self, instrument: UniverseInstrument, lookback_days: int
    ) -> List[Candle]:
        symbol_str = instrument.symbol.symbol
        if symbol_str in self.scenarios:
            candles = self.scenarios[symbol_str]
            if candles is None:
                raise MissingDataQualityDataError(f"No data for {symbol_str}")
            return candles

        # Default perfect 252 day history (Mon-Fri)
        candles = []
        end_date = datetime.now(timezone.utc) - timedelta(days=1)

        # We need to generate 252 trading days. We'll just generate the last ~350 calendar days
        # and pick weekdays until we have 252 candles.
        days_generated = 0
        current_date = end_date
        while days_generated < 252:
            if current_date.weekday() < 5:
                candles.append(
                    Candle(
                        symbol=instrument.symbol,
                        timeframe=Timeframe.D1,
                        timestamp=current_date,
                        open=100.0,
                        high=105.0,
                        low=95.0,
                        close=100.0,
                        volume=1000000.0,
                        is_completed=True,
                    )
                )
                days_generated += 1
            current_date -= timedelta(days=1)

        # Ensure earliest candle is at the beginning of the list to mimic historical order
        return sorted(candles, key=lambda c: c.timestamp)

    async def get_dataset_version(self, instrument: UniverseInstrument) -> str:
        return "1.0.0"


class MockMarketCalendarProvider(IMarketCalendarProvider):
    async def get_expected_trading_sessions(
        self, instrument: UniverseInstrument, start_date: date, end_date: date
    ) -> Set[date]:
        # Simple mock: Monday-Friday are expected, no holidays
        sessions = set()
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:
                sessions.add(current_date)
            current_date += timedelta(days=1)
        return sessions


class MockCorporateActionProvider(ICorporateActionProvider):
    def __init__(self, override_validity=None):
        self.override_validity = override_validity or {}

    async def verify_adjustments_applied(
        self,
        instrument: UniverseInstrument,
        candles: List[Candle],
        dataset_version: str,
    ) -> bool:
        return self.override_validity.get(instrument.symbol.symbol, True)


@pytest.fixture
def mock_dq_data_provider():
    return MockDataQualityDataProvider()


@pytest.fixture
def mock_calendar_provider():
    return MockMarketCalendarProvider()


@pytest.fixture
def mock_corporate_action_provider():
    return MockCorporateActionProvider()


@pytest.fixture
def sample_instrument():
    exchange = ExchangeReference(code="XNAS")
    symbol = SymbolReference(symbol="AAPL", exchange=exchange)
    return UniverseInstrument(
        symbol=symbol,
        instrument_type=InstrumentType.EQUITY,
        trading_status=TradingStatus.ACTIVE,
        market_segment=MarketSegment.EQUITY_CASH,
        is_delisted=False,
    )
