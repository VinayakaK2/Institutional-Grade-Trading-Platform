import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.certification.pipeline import CertificationPipeline
from backend.data_validation.validation.engine import ValidationEngine
from backend.data_validation.validation.rules.structural import StructuralRule
from backend.data_validation.validation.rules.ohlcv import OhlcvRule
from backend.data_validation.cleaning.engine import CleaningEngine
from backend.data_validation.cleaning.rules.basic import DuplicateRemovalRule
from backend.data_validation.contracts.rule import ValidationContext
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage
from backend.data_validation.infrastructure.storage import PostgreSQLQuarantineStorage
from backend.application.uow.sqlalchemy import SqlAlchemyUnitOfWork
from backend.historical_data.exceptions import StorageException

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
def advanced_pipeline(db_session, setup_database):
    uow = DummyUoW(db_session)
    storage = PostgreSQLHistoricalStorage(uow)
    quarantine = PostgreSQLQuarantineStorage(uow)
    val_engine = ValidationEngine([StructuralRule(), OhlcvRule()])
    clean_engine = CleaningEngine([DuplicateRemovalRule()])
    return CertificationPipeline(storage, quarantine, val_engine, clean_engine, batch_size=100)

@pytest.mark.asyncio
async def test_canonical_storage_strict_boundaries(advanced_pipeline, db_session):
    sym = SymbolReference(symbol="STRICT", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test")
    
    async def stream():
        # Valid
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=100)
        # Missing field (structural)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-02T00:00:00Z", raw_open=10, raw_high=None, raw_low=9, raw_close=11, raw_volume=100)
        # Invalid OHLC (High < Low)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-03T00:00:00Z", raw_open=10, raw_high=5, raw_low=9, raw_close=11, raw_volume=100)
        # Negative Vol
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-04T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=-50)
        # Duplicate of Valid
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=100)

    certified = await advanced_pipeline.process_stream(stream(), context)
    assert certified == 1 # Only 1 valid

    res = await db_session.execute(text("SELECT count(*) FROM canonical_candles WHERE symbol_id = 'STRICT'"))
    assert res.scalar() == 1
    
    res = await db_session.execute(text("SELECT count(*) FROM quarantined_candles WHERE symbol_id = 'STRICT'"))
    assert res.scalar() == 4

@pytest.mark.asyncio
async def test_quarantine_idempotency_and_preservation(advanced_pipeline, db_session):
    sym = SymbolReference(symbol="IDEM", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test")
    
    async def stream():
        # Send same invalid record multiple times
        for _ in range(5):
            yield RawCandle(
                provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", 
                raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=-50, extra_data={"test": "payload"}
            )
            
    await advanced_pipeline.process_stream(stream(), context)
    
    # Should only be 1 in quarantine due to ON CONFLICT DO NOTHING idempotency
    res = await db_session.execute(text("SELECT count(*) FROM quarantined_candles WHERE symbol_id = 'IDEM'"))
    assert res.scalar() == 1
        # Verify payload preservation & reason
    row = (await db_session.execute(text("SELECT extra_data, quarantine_reason FROM quarantined_candles WHERE symbol_id = 'IDEM'"))).fetchone()
        
    extra_data = row[0]
    if isinstance(extra_data, str):
        import json
        extra_data = json.loads(extra_data)
            
    assert extra_data["test"] == "payload"
    assert "Failed certification" in row[1]

@pytest.mark.asyncio
async def test_failure_recovery_rollback(advanced_pipeline, db_session):
    sym = SymbolReference(symbol="FAIL", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test")
    
    async def stream():
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=100)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-02T00:00:00Z", raw_open=10, raw_high=12, raw_low=9, raw_close=11, raw_volume=100)
    
    # Mock Canonical Storage to fail
    with patch.object(advanced_pipeline._storage, 'save_normalized_candles', side_effect=StorageException("DB Failure")):
        with pytest.raises(StorageException):
            await advanced_pipeline.process_stream(stream(), context)
            
    # Verify complete rollback (nothing in canonical)
    res = await db_session.execute(text("SELECT count(*) FROM canonical_candles WHERE symbol_id = 'FAIL'"))
    assert res.scalar() == 0
