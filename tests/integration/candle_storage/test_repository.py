"""
Integration Tests for Candle Repository
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.infrastructure.database.orm.base import Base
from backend.candle_storage.infrastructure.repository import PostgreSQLCandleRepository
from backend.candle_storage.models.dataset import CandleQueryFilters, DatasetType
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.application.uow.base import BaseUnitOfWork

# Import all ORMs to ensure they are bound to Base

from sqlalchemy.pool import StaticPool

# Test Database Setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False, 
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


class TestUnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session = None
        
    async def __aenter__(self):
        self._session = self._session_factory()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
        
    async def commit(self):
        await self._session.commit()
        
    async def rollback(self):
        await self._session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    print(f"Base metadata tables: {Base.metadata.tables.keys()}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def uow(test_db):
    return TestUnitOfWork(TestingSessionLocal)


@pytest_asyncio.fixture(scope="function")
async def repository(uow):
    return PostgreSQLCandleRepository(uow)

@pytest.fixture
def sample_symbol():
    from backend.market_data.models.symbol import ExchangeReference
    return SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))

@pytest.fixture
def isolation_symbol():
    from backend.market_data.models.symbol import ExchangeReference
    return SymbolReference(symbol="ISOLATION", exchange=ExchangeReference(code="NASDAQ"))

@pytest.fixture
def del_symbol():
    from backend.market_data.models.symbol import ExchangeReference
    return SymbolReference(symbol="DEL", exchange=ExchangeReference(code="NASDAQ"))


@pytest.mark.asyncio
async def test_repository_save_and_query_canonical(repository, uow, sample_symbol):
    candles = [
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=100.0, high=105.0, low=95.0, close=102.0, volume=1000.0, is_completed=True
        ),
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 2, tzinfo=timezone.utc),
            open=102.0, high=110.0, low=101.0, close=108.0, volume=1500.0, is_completed=True
        )
    ]
    
    # Save
    async with uow:
        await repository.save_batch(DatasetType.CANONICAL, None, candles)
        
    # Idempotent write should not fail
    async with uow:
        await repository.save_batch(DatasetType.CANONICAL, None, candles)
        
    # Query
    filters = CandleQueryFilters(
        symbol=sample_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.CANONICAL,
        start_time=datetime(2023, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2023, 1, 2, tzinfo=timezone.utc),
        limit=10,
        order_by_desc=True
    )
    
    results = []
    async with uow:
        async for c in repository.get_stream(filters):
            results.append(c)
            
    assert len(results) == 2
    assert results[0].close == 108.0
    assert results[1].close == 102.0


@pytest.mark.asyncio
async def test_repository_save_and_query_adjusted(repository, uow, sample_symbol):
    version = "v1"
    candles = [
        Candle(
            symbol=sample_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=50.0, high=52.5, low=47.5, close=51.0, volume=2000.0, is_completed=True # Adjusted via split
        )
    ]
    
    async with uow:
        await repository.save_batch(DatasetType.ADJUSTED, version, candles)
        
    filters = CandleQueryFilters(
        symbol=sample_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.ADJUSTED,
        dataset_version=version
    )
    
    results = []
    async with uow:
        async for c in repository.get_stream(filters):
            results.append(c)
            
    assert len(results) == 1
    assert results[0].close == 51.0


@pytest.mark.asyncio
async def test_dataset_isolation(repository, uow, isolation_symbol):
    """
    Regression Test Scenario:
    Verify Raw, Canonical, and Adjusted datasets remain completely isolated.
    Note: In production (PostgreSQL), these datasets are physically isolated 
    into separate tables/partitions which guarantees complete isolation 
    under concurrent read and write operations.
    """
    raw_candles = [
        RawCandle(
            provider="test",
            symbol=isolation_symbol,
            timeframe=Timeframe.D1,
            raw_timestamp=str(datetime(2023, 1, 1, tzinfo=timezone.utc)),
            raw_open=100.0, raw_high=100.0, raw_low=100.0, raw_close=100.0, raw_volume=100.0,
            extra_data={}
        )
    ]
    
    canonical_candles = [
        Candle(
            symbol=isolation_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=101.0, high=101.0, low=101.0, close=101.0, volume=101.0, is_completed=True
        )
    ]
    
    adjusted_candles = [
        Candle(
            symbol=isolation_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=50.0, high=50.0, low=50.0, close=50.0, volume=202.0, is_completed=True
        )
    ]
    
    # Save all three
    async with uow:
        await repository.save_batch(DatasetType.RAW, None, raw_candles)
        await repository.save_batch(DatasetType.CANONICAL, None, canonical_candles)
        await repository.save_batch(DatasetType.ADJUSTED, "v1", adjusted_candles)
        
    # Query each and assert no crosstalk
    async with uow:
        # RAW
        f_raw = CandleQueryFilters(
            symbol=isolation_symbol, 
            timeframe=Timeframe.D1, 
            dataset_type=DatasetType.RAW,
            start_time=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 2, tzinfo=timezone.utc)
        )
        res_raw = [c async for c in repository.get_stream(f_raw)]
        assert len(res_raw) == 1
        assert res_raw[0].raw_close == 100.0
        
        # CANONICAL
        f_canon = CandleQueryFilters(symbol=isolation_symbol, timeframe=Timeframe.D1, dataset_type=DatasetType.CANONICAL)
        res_canon = [c async for c in repository.get_stream(f_canon)]
        assert len(res_canon) == 1
        assert res_canon[0].close == 101.0
        
        # ADJUSTED
        f_adj = CandleQueryFilters(symbol=isolation_symbol, timeframe=Timeframe.D1, dataset_type=DatasetType.ADJUSTED, dataset_version="v1")
        res_adj = [c async for c in repository.get_stream(f_adj)]
        assert len(res_adj) == 1
        assert res_adj[0].close == 50.0



@pytest.mark.asyncio
async def test_dataset_deletion(repository, uow, del_symbol):
    candles = [
        Candle(
            symbol=del_symbol,
            timeframe=Timeframe.D1,
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            open=1.0, high=1.0, low=1.0, close=1.0, volume=1.0, is_completed=True
        )
    ]
    
    async with uow:
        await repository.save_batch(DatasetType.CANONICAL, None, candles)
        await repository.delete_dataset(DatasetType.CANONICAL, del_symbol.symbol, "1d")
        
    filters = CandleQueryFilters(
        symbol=del_symbol,
        timeframe=Timeframe.D1,
        dataset_type=DatasetType.CANONICAL
    )
    
    async with uow:
        results = [c async for c in repository.get_stream(filters)]
        assert len(results) == 0
