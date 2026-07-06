import pytest
import asyncio
from datetime import datetime
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType, IndicatorQueryFilters
from backend.indicator_engine.infrastructure.repository import PostgreSQLIndicatorRepository
from backend.indicator_engine.engine.query import IndicatorQueryEngine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.database.orm.base import Base

import pytest_asyncio

class DummyUOW:
    def __init__(self, session):
        self._session = session

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session = SessionLocal()
    yield session
    await session.close()

@pytest.fixture
def repo(async_session):
    return PostgreSQLIndicatorRepository(DummyUOW(async_session))

@pytest.mark.asyncio
async def test_indicator_repository_save_and_query(repo):
    symbol = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    dt1 = datetime(2023, 1, 1)
    dt2 = datetime(2023, 1, 2)
    
    ind1 = IndicatorResult(
        symbol=symbol,
        timeframe=tf,
        dataset_version="canonical",
        timestamp=dt1,
        indicator_type=IndicatorType.SMA,
        parameters={"period": 14},
        value=150.5
    )
    
    ind2 = IndicatorResult(
        symbol=symbol,
        timeframe=tf,
        dataset_version="canonical",
        timestamp=dt2,
        indicator_type=IndicatorType.SMA,
        parameters={"period": 14},
        value=151.0
    )
    
    await repo.save_batch([ind1, ind2])
    # Idempotent save test
    await repo.save_batch([ind1, ind2])
    
    filters = IndicatorQueryFilters(
        symbol=symbol,
        timeframe=tf,
        dataset_version="canonical",
        indicator_type=IndicatorType.SMA,
        parameters={"period": 14}
    )
    
    results = []
    async for r in repo.get_stream(filters):
        results.append(r)
        
    assert len(results) == 2
    assert results[0].value == 150.5
    assert results[1].value == 151.0
    
    # Test latest timestamp
    latest = await repo.get_latest_timestamp(filters)
    assert latest == str(dt2)

@pytest.mark.asyncio
async def test_indicator_query_engine(repo):
    query_engine = IndicatorQueryEngine(repo)
    symbol = SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ"))
    
    ind1 = IndicatorResult(
        symbol=symbol,
        timeframe=Timeframe.D1,
        dataset_version="canonical",
        timestamp=datetime(2023, 1, 1),
        indicator_type=IndicatorType.EMA,
        parameters={"period": 20},
        value=10.0,
        internal_state={"ema": 10.0}
    )
    
    await repo.save_batch([ind1])
    
    filters = IndicatorQueryFilters(
        symbol=symbol,
        timeframe=Timeframe.D1,
        dataset_version="canonical",
        indicator_type=IndicatorType.EMA,
        parameters={"period": 20}
    )
    
    results = []
    async for r in query_engine.query(filters):
        results.append(r)
        
    assert len(results) == 1
    assert results[0].internal_state == {"ema": 10.0}
