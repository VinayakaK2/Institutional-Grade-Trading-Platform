import pytest
from backend.historical_data.engine.normalizer import DataNormalizer
from backend.historical_data.exceptions import NormalizationException, StorageException
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage

def test_normalizer_exceptions(dummy_symbol):
    from backend.historical_data.models.raw import RawCandle
    from backend.market_data.models.timeframe import Timeframe
    raw = RawCandle(
        provider="mock",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        raw_timestamp="invalid",
        raw_open=1, raw_high=1, raw_low=1, raw_close=1, raw_volume=1
    )
    with pytest.raises(NormalizationException):
        DataNormalizer.normalize(raw)

from backend.market_data.models.symbol import SymbolReference, ExchangeReference

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ"))

@pytest.mark.asyncio
async def test_postgres_exceptions(dummy_symbol):
    from datetime import datetime
    from backend.historical_data.models.raw import RawCandle
    from backend.market_data.models.timeframe import Timeframe
    raw = RawCandle(
        provider="mock",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        raw_timestamp="2024-01-01T00:00:00Z",
        raw_open=1, raw_high=1, raw_low=1, raw_close=1, raw_volume=1
    )
    
    storage = PostgreSQLHistoricalStorage(None)
    with pytest.raises(StorageException):
        await storage.save_raw_candles([raw])
        
    candle = DataNormalizer.normalize(raw)
    with pytest.raises(StorageException):
        await storage.save_normalized_candles([candle])
        
    with pytest.raises(StorageException):
        async for c in storage.get_raw_candles(dummy_symbol, Timeframe.H1, datetime(2024,1,1), datetime(2024,1,2)):
            pass
            
    from backend.historical_data.models.metadata import DownloadMetadata
    meta = DownloadMetadata(
        request_id="abc",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        provider="mock",
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,1,2)
    )
    with pytest.raises(StorageException):
        await storage.save_metadata(meta)
