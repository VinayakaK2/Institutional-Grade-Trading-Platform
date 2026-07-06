import pytest
from backend.data_validation.infrastructure.storage import PostgreSQLQuarantineStorage
from backend.historical_data.exceptions import StorageException
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe

class DummyBind:
    class DummyDialect:
        name = "sqlite"
    dialect = DummyDialect()

class DummySession:
    bind = DummyBind()
    def __init__(self):
        self.executed = False
    async def execute(self, stmt):
        self.executed = True

class DummyUoW:
    _session = DummySession()

@pytest.mark.asyncio
async def test_quarantine_storage_empty():
    storage = PostgreSQLQuarantineStorage(DummyUoW())
    await storage.save_quarantined_candles([], "test")

@pytest.mark.asyncio
async def test_quarantine_storage_save():
    uow = DummyUoW()
    storage = PostgreSQLQuarantineStorage(uow)
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    candles = [
        RawCandle(provider="test", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z",
                 raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
    ]
    await storage.save_quarantined_candles(candles, "Failed Validation")
    assert uow._session.executed == True

@pytest.mark.asyncio
async def test_quarantine_storage_no_session():
    class BadUoW:
        pass
    storage = PostgreSQLQuarantineStorage(BadUoW())
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    candles = [
        RawCandle(provider="test", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z",
                 raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
    ]
    with pytest.raises(StorageException):
        await storage.save_quarantined_candles(candles, "Failed Validation")
