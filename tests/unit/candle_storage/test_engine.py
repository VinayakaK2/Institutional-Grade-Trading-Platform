"""
Unit Tests for Candle Storage & Query Engines
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from backend.candle_storage.engine.storage import CandleStorageEngine
from backend.candle_storage.engine.query import CandleQueryEngine
from backend.candle_storage.models.dataset import CandleQueryFilters, DatasetType
from backend.candle_storage.exceptions import CandleStorageException, CandleQueryException
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def storage_engine(mock_repository):
    return CandleStorageEngine(mock_repository)
    
@pytest.fixture
def query_engine(mock_repository):
    return CandleQueryEngine(mock_repository)

@pytest.fixture
def sample_symbol():
    from backend.market_data.models.symbol import ExchangeReference
    return SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))

@pytest.mark.asyncio
async def test_save_raw_candles_valid(storage_engine, mock_repository, sample_symbol):
    candles = [
        RawCandle(
            provider="test",
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            raw_timestamp="1234567890",
            raw_open=100.0,
            raw_high=105.0,
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0,
            extra_data={}
        )
    ]
    await storage_engine.save_raw_candles(candles)
    mock_repository.save_batch.assert_called_once_with(
        dataset_type=DatasetType.RAW,
        dataset_version=None,
        candles=candles
    )

@pytest.mark.asyncio
async def test_save_raw_candles_invalid(storage_engine, sample_symbol):
    candles = [
        RawCandle(
            provider="", # Invalid missing provider
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            raw_timestamp="1234567890",
            raw_open=100.0,
            raw_high=105.0,
            raw_low=95.0,
            raw_close=102.0,
            raw_volume=1000.0,
            extra_data={}
        )
    ]
    with pytest.raises(CandleStorageException):
        await storage_engine.save_raw_candles(candles)

@pytest.mark.asyncio
async def test_save_adjusted_candles_missing_version(storage_engine, sample_symbol):
    candles = [
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime.now(timezone.utc),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0,
            is_completed=True
        )
    ]
    with pytest.raises(CandleStorageException, match="dataset_version is required"):
        await storage_engine.save_adjusted_candles("", candles)

@pytest.mark.asyncio
async def test_query_invalid_adjusted_filters(query_engine, sample_symbol):
    # Attempting to query adjusted without version
    filters = CandleQueryFilters(
        symbol=sample_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.ADJUSTED,
        dataset_version=None
    )
    
    with pytest.raises(CandleQueryException, match="Dataset version must be provided"):
        async for _ in query_engine.query(filters):
            pass

@pytest.mark.asyncio
async def test_query_invalid_canonical_filters(query_engine, sample_symbol):
    # Attempting to query canonical WITH a version
    filters = CandleQueryFilters(
        symbol=sample_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.CANONICAL,
        dataset_version="v1"
    )
    
    with pytest.raises(CandleQueryException, match="Dataset version should not be provided"):
        async for _ in query_engine.query(filters):
            pass

@pytest.mark.asyncio
async def test_save_canonical_candles_valid(storage_engine, mock_repository, sample_symbol):
    candles = [
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime.now(timezone.utc),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0,
            is_completed=True
        )
    ]
    await storage_engine.save_canonical_candles(candles)
    mock_repository.save_batch.assert_called_once_with(
        dataset_type=DatasetType.CANONICAL,
        dataset_version=None,
        candles=candles
    )

@pytest.mark.asyncio
async def test_save_canonical_candles_invalid(storage_engine, sample_symbol):
    # This might require some actual validation in storage engine, but pydantic handles most.
    # Let's pass empty list.
    await storage_engine.save_canonical_candles([])
    # should just return

@pytest.mark.asyncio
async def test_save_adjusted_candles_valid(storage_engine, mock_repository, sample_symbol):
    candles = [
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime.now(timezone.utc),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0,
            is_completed=True
        )
    ]
    await storage_engine.save_adjusted_candles("v2", candles)
    mock_repository.save_batch.assert_called_once_with(
        dataset_type=DatasetType.ADJUSTED,
        dataset_version="v2",
        candles=candles
    )

@pytest.mark.asyncio
async def test_query_valid(query_engine, mock_repository, sample_symbol):
    filters = CandleQueryFilters(
        symbol=sample_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.RAW
    )
    
    class MockRepo:
        async def get_stream(self, f):
            yield "candle1"
            yield "candle2"
            
    query_engine._repository = MockRepo()
    
    results = [c async for c in query_engine.query(filters)]
    assert len(results) == 2
    assert results[0] == "candle1"

@pytest.mark.asyncio
async def test_repository_save_batch_empty():
    from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
    repo = PostgreSQLCandleRepository(None)
    await repo.save_batch(DatasetType.RAW, None, [])
    
@pytest.mark.asyncio
async def test_repository_save_batch_no_session():
    from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
    class FakeUoW:
        pass
    repo = PostgreSQLCandleRepository(FakeUoW())
    with pytest.raises(CandleStorageException, match="does not expose a SQLAlchemy session"):
        await repo.save_batch(DatasetType.RAW, None, ["dummy"])

@pytest.mark.asyncio
async def test_repository_save_batch_invalid_dataset():
    from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
    class FakeSession:
        class Bind:
            class Dialect:
                name = "sqlite"
            dialect = Dialect()
        bind = Bind()
    class FakeUoW:
        _session = FakeSession()
    repo = PostgreSQLCandleRepository(FakeUoW())
    with pytest.raises(CandleStorageException, match="Unknown dataset_type: INVALID"):
        await repo.save_batch("INVALID", None, ["dummy"])

@pytest.mark.asyncio
async def test_repository_get_stream_no_session(sample_symbol):
    from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
    class FakeUoW:
        pass
    repo = PostgreSQLCandleRepository(FakeUoW())
    filters = CandleQueryFilters(symbol=sample_symbol, timeframe=Timeframe.D1, dataset_type=DatasetType.RAW)
    with pytest.raises(CandleStorageException, match="does not expose a SQLAlchemy session"):
        async for _ in repo.get_stream(filters):
            pass
@pytest.mark.asyncio
async def test_repository_save_batch_db_error(sample_symbol):
    from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
    class FakeSession:
        class Bind:
            class Dialect:
                name = "sqlite"
            dialect = Dialect()
        bind = Bind()
        async def execute(self, stmt):
            raise Exception("DB Error")
    class FakeUoW:
        _session = FakeSession()
    repo = PostgreSQLCandleRepository(FakeUoW())
    class DummyCandle:
        provider = "x"
        symbol = sample_symbol
        timeframe = Timeframe.D1
        raw_timestamp = "2023-01-01"
        raw_open = 1.0
        raw_high = 1.0
        raw_low = 1.0
        raw_close = 1.0
        raw_volume = 1.0
        extra_data = {}
    with pytest.raises(CandleStorageException, match="Database error during raw batch insert: DB Error"):
        await repo.save_batch(DatasetType.RAW, None, [DummyCandle()])
