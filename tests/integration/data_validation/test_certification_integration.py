import pytest
import asyncio
from datetime import datetime, date
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.certification.pipeline import CertificationPipeline
from backend.data_validation.validation.engine import ValidationEngine
from backend.data_validation.validation.rules.structural import StructuralRule
from backend.data_validation.validation.rules.ohlcv import OhlcvRule
from backend.data_validation.detectors.anomalies import AnomalyDetector
from backend.data_validation.cleaning.engine import CleaningEngine
from backend.data_validation.cleaning.rules.basic import DuplicateRemovalRule, WhitespaceCleanupRule
from backend.data_validation.contracts.rule import ValidationContext
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage
from backend.data_validation.infrastructure.storage import PostgreSQLQuarantineStorage
from backend.application.uow.sqlalchemy import SqlAlchemyUnitOfWork

class DummyUoW(SqlAlchemyUnitOfWork):
    def __init__(self, session):
        self._session = session
        
    async def commit(self):
        await self._session.commit()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()

@pytest.fixture
def certification_pipeline(db_session, setup_database):
    uow = DummyUoW(db_session)
    storage = PostgreSQLHistoricalStorage(uow)
    quarantine = PostgreSQLQuarantineStorage(uow)
    
    val_engine = ValidationEngine([StructuralRule(), OhlcvRule(), AnomalyDetector()])
    clean_engine = CleaningEngine([DuplicateRemovalRule(), WhitespaceCleanupRule()])
    
    return CertificationPipeline(storage, quarantine, val_engine, clean_engine, batch_size=100)

@pytest.mark.asyncio
async def test_full_certification_lifecycle(certification_pipeline, db_session):
    sym = SymbolReference(symbol="TEST_CERT", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test", dependencies={"anomaly_config": {}})
    
    async def stream():
        # 1. Valid record
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
        # 2. Duplicate (should be quarantined/rejected by cleaner)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
        # 3. Invalid Structural (null open) -> Should be quarantined
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-02T00:00:00Z", raw_open=None, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
        # 4. Invalid OHLCV (High < Low) -> Should be quarantined
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-03T00:00:00Z", raw_open=1, raw_high=0.5, raw_low=1, raw_close=2, raw_volume=10)
        # 5. Valid record
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-04T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=100)

    certified_count = await certification_pipeline.process_stream(stream(), context)
    
    assert certified_count == 2 # Only #1 and #5 should survive
    
    # Verify DB state
    from sqlalchemy import text
    
    # 2 Canonical Records
    res = await db_session.execute(text("SELECT count(*) FROM canonical_candles WHERE symbol_id = 'TEST_CERT'"))
    assert res.scalar() == 2
    
    # 3 Quarantined Records (#2 Duplicate, #3 Structural Null, #4 OHLCV Failure)
    res = await db_session.execute(text("SELECT count(*) FROM quarantined_candles WHERE symbol_id = 'TEST_CERT'"))
    assert res.scalar() == 3
