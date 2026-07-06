import pytest
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage
from backend.historical_data.exceptions import StorageException
from backend.historical_data.models.metadata import DownloadMetadata, DownloadStatus
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from datetime import datetime

class MockSession:
    def __init__(self, dialect_name="postgres", raise_on_execute=False):
        class Bind:
            class Dialect:
                pass
        self.bind = Bind()
        self.bind.dialect = Bind.Dialect()
        self.bind.dialect.name = dialect_name
        self.raise_on_execute = raise_on_execute
        
    async def execute(self, stmt):
        if self.raise_on_execute:
            raise Exception("Mock execute error")

class MockUoW:
    def __init__(self, session):
        self._session = session

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ"))

@pytest.mark.asyncio
async def test_postgres_exceptions(dummy_symbol):
    session = MockSession(dialect_name="postgres", raise_on_execute=True)
    storage = PostgreSQLHistoricalStorage(MockUoW(session))
    
    raw = RawCandle(provider="mock", symbol=dummy_symbol, timeframe=Timeframe.D1, raw_timestamp="2024", raw_open=1, raw_high=1, raw_low=1, raw_close=1, raw_volume=1, extra_data={})
    with pytest.raises(StorageException):
        await storage.save_raw_candles([raw])
        
    candle = Candle(symbol=dummy_symbol, timeframe=Timeframe.D1, timestamp=datetime(2024,1,1), open=1, high=1, low=1, close=1, volume=1)
    with pytest.raises(StorageException):
        await storage.save_normalized_candles([candle])
        
    meta = DownloadMetadata(request_id="req", symbol=dummy_symbol, timeframe=Timeframe.D1, start_date=datetime(2024,1,1), end_date=datetime(2024,1,2), provider="mock")
    with pytest.raises(StorageException):
        await storage.save_metadata(meta)
