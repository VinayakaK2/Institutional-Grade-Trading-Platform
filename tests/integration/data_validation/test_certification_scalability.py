import pytest
import asyncio
import time
import tracemalloc
from datetime import datetime, timedelta
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
        pass # mock commit
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockHistoricalStorage:
    async def save_normalized_candles(self, candles):
        pass # Mock insert

class MockQuarantineStorage:
    async def save_quarantined_candles(self, raw_candles, reason: str):
        pass

@pytest.fixture
def scalable_pipeline():
    storage = MockHistoricalStorage()
    quarantine = MockQuarantineStorage()
    val_engine = ValidationEngine([StructuralRule(), OhlcvRule(), AnomalyDetector()])
    clean_engine = CleaningEngine([DuplicateRemovalRule(), WhitespaceCleanupRule()])
    
    return CertificationPipeline(storage, quarantine, val_engine, clean_engine, batch_size=5000)

@pytest.mark.asyncio
async def test_scalability_10000_candles(scalable_pipeline):
    sym = SymbolReference(symbol="SCALE10K", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test", dependencies={"anomaly_config": {}})
    
    async def generate_candles(count):
        base_time = datetime(2020, 1, 1)
        for i in range(count):
            yield RawCandle(
                provider="test",
                symbol=sym,
                timeframe=tf,
                raw_timestamp=(base_time + timedelta(days=i)).isoformat() + "Z",
                raw_open=100.0,
                raw_high=105.0,
                raw_low=95.0,
                raw_close=102.0,
                raw_volume=1000
            )

    tracemalloc.start()
    start = time.time()
    certified = await scalable_pipeline.process_stream(generate_candles(10000), context)
    duration = time.time() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert certified == 10000
    assert duration < 15.0 # Should easily process 10k in < 15 seconds
    assert peak_memory < 100 * 1024 * 1024 # < 100MB

@pytest.mark.asyncio
async def test_scalability_100000_candles(scalable_pipeline):
    sym = SymbolReference(symbol="SCALE100K", exchange=ExchangeReference(code="NYSE"))
    tf = Timeframe.M1 # Minute data
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test", dependencies={"anomaly_config": {}})
    
    async def generate_candles(count):
        base_time = datetime(2020, 1, 1)
        for i in range(count):
            # inject a few invalid ones
            if i % 100 == 0:
                # invalid OHLC
                yield RawCandle(provider="test", symbol=sym, timeframe=tf, raw_timestamp=(base_time + timedelta(minutes=i)).isoformat() + "Z", raw_open=10, raw_high=5, raw_low=9, raw_close=11, raw_volume=100)
            else:
                yield RawCandle(provider="test", symbol=sym, timeframe=tf, raw_timestamp=(base_time + timedelta(minutes=i)).isoformat() + "Z", raw_open=100.0, raw_high=105.0, raw_low=95.0, raw_close=102.0, raw_volume=1000)

    tracemalloc.start()
    start = time.time()
    certified = await scalable_pipeline.process_stream(generate_candles(100000), context)
    duration = time.time() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # We injected 1 invalid every 100
    assert certified == 99000
    assert duration < 120.0 # Should easily process 100k in < 120 seconds
    assert peak_memory < 200 * 1024 * 1024 # < 200MB
