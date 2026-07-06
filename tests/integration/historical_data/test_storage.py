import pytest
from datetime import datetime
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage
from backend.application.uow.sqlalchemy import SqlAlchemyUnitOfWork
from backend.historical_data.orm.models import RawCandleOrm, CandleOrm
from backend.historical_data.engine.normalizer import DataNormalizer
from sqlalchemy import select, func, text

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="TSLA", exchange=ExchangeReference(name="NASDAQ", code="NASDAQ"))

@pytest.mark.asyncio
async def test_postgres_storage_idempotent_insert(engine, setup_database, db_session, dummy_symbol):
    # Setup Unit of Work pointing to the test DB session
    class DummyUoW(SqlAlchemyUnitOfWork):
        def __init__(self, session):
            self._session = session
            self._repositories = {}
            
        async def commit(self):
            await self._session.commit()
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    uow = DummyUoW(db_session)
    storage = PostgreSQLHistoricalStorage(uow)
    
    raw_candle = RawCandle(
        provider="test",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        raw_timestamp="2024-01-01T10:00:00Z",
        raw_open=200.0,
        raw_high=205.0,
        raw_low=195.0,
        raw_close=202.0,
        raw_volume=5000.0,
        extra_data={"trades": 10}
    )
    
    # 1. First Insert Raw
    await storage.save_raw_candles([raw_candle])
    await uow.commit()
    
    # Verify
    from sqlalchemy import select, func
    res = await db_session.execute(select(func.count(RawCandleOrm.id)))
    count = res.scalar()
    assert count == 1
    
    # 2. Idempotent Insert Raw
    await storage.save_raw_candles([raw_candle])
    # Should still be 1 (ON CONFLICT DO NOTHING worked)
    await uow.commit()
    res = await db_session.execute(select(func.count(RawCandleOrm.id)))
    count = res.scalar()
    assert count == 1
    
    # 3. Normalize and Insert Normalized
    candle = DataNormalizer.normalize(raw_candle)
    await storage.save_normalized_candles([candle])
    await uow.commit()
    
    res = await db_session.execute(select(func.count(CandleOrm.id)))
    count = res.scalar()
    assert count == 1
    
    # 4. Idempotent Normalized
    await storage.save_normalized_candles([candle])
    await uow.commit()
    
    res = await db_session.execute(select(func.count(CandleOrm.id)))
    count = res.scalar()
    assert count == 1

class DummyUoW(SqlAlchemyUnitOfWork):
    def __init__(self, session):
        self._session = session
        self._repositories = {}
        
    async def commit(self):
        await self._session.commit()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_postgres_storage_metadata_idempotency(engine, setup_database, db_session, dummy_symbol):
    uow = DummyUoW(db_session)
    storage = PostgreSQLHistoricalStorage(uow)
    
    from backend.historical_data.models.metadata import DownloadMetadata, DownloadStatus
    from datetime import datetime
    
    meta = DownloadMetadata(
        request_id="test_req_123",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        provider="mock",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2)
    )
    
    # Save first time
    meta.status = DownloadStatus.IN_PROGRESS
    await storage.save_metadata(meta)
    
    # Save second time, should UPSERT
    meta.status = DownloadStatus.COMPLETED
    meta.records_saved = 50
    await storage.save_metadata(meta)
    
    from backend.historical_data.orm.models import DownloadMetadataOrm
    from sqlalchemy import select
    
    stmt = select(DownloadMetadataOrm).where(DownloadMetadataOrm.request_id == "test_req_123")
    result = await db_session.execute(stmt)
    records = result.scalars().all()
    
    assert len(records) == 1
    assert records[0].status == "COMPLETED"
    assert records[0].records_saved == 50

@pytest.mark.asyncio
async def test_postgres_storage_replay(engine, setup_database, db_session, dummy_symbol):
    uow = DummyUoW(db_session)
    storage = PostgreSQLHistoricalStorage(uow)
    
    raw = RawCandle(
        provider="mock",
        symbol=dummy_symbol,
        timeframe=Timeframe.H1,
        raw_timestamp="2024-01-01T10:00:00Z",
        raw_open=100.0,
        raw_high=105.0,
        raw_low=95.0,
        raw_close=102.0,
        raw_volume=1000.0,
        extra_data={}
    )
    
    # Save raw
    await storage.save_raw_candles([raw])
    await uow.commit()
    
    # Replay
    fetched = []
    async for candle in storage.get_raw_candles(dummy_symbol, Timeframe.H1, datetime(2024, 1, 1), datetime(2024, 1, 2)):
        fetched.append(candle)
        
    assert len(fetched) == 1
    assert fetched[0].raw_timestamp == "2024-01-01T10:00:00Z"
    assert fetched[0].raw_close == 102.0
