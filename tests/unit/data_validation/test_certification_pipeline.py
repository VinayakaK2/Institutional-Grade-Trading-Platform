import pytest
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.certification.pipeline import CertificationPipeline
from backend.data_validation.validation.engine import ValidationEngine
from backend.data_validation.validation.rules.structural import StructuralRule
from backend.data_validation.cleaning.engine import CleaningEngine
from backend.data_validation.contracts.rule import ValidationContext
from backend.historical_data.contracts.storage import HistoricalStorageContract
from backend.data_validation.contracts.storage import QuarantineStorageContract

class DummyStorage(HistoricalStorageContract):
    def __init__(self):
        self.raw_saved = []
        self.canonical_saved = []
    async def save_raw_candles(self, candles):
        self.raw_saved.extend(candles)
    async def save_normalized_candles(self, candles):
        self.canonical_saved.extend(candles)
    async def get_raw_candles(self, symbol, timeframe, start, end):
        for c in self.raw_saved:
            yield c
    async def save_metadata(self, metadata):
        pass

class DummyQuarantine(QuarantineStorageContract):
    def __init__(self):
        self.quarantined = []
    async def save_quarantined_candles(self, candles, reason=""):
        self.quarantined.extend(candles)

@pytest.mark.asyncio
async def test_certification_pipeline():
    storage = DummyStorage()
    quarantine = DummyQuarantine()
    validation = ValidationEngine([StructuralRule()])
    cleaning = CleaningEngine([]) # No cleaning rules, just pass through valid
    
    pipeline = CertificationPipeline(storage, quarantine, validation, cleaning, batch_size=2)
    
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    context = ValidationContext(symbol=sym, timeframe=tf, provider="test")
    
    async def stream():
        # 1 valid, 1 invalid (null open)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01T00:00:00Z", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
        yield RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-02T00:00:00Z", raw_open=None, raw_high=2, raw_low=1, raw_close=2, raw_volume=10)
        
    certified = await pipeline.process_stream(stream(), context)
    
    assert certified == 1
    assert len(storage.canonical_saved) == 1
    assert storage.canonical_saved[0].timestamp.isoformat() == "2024-01-01T00:00:00+00:00"
    
    assert len(quarantine.quarantined) == 1
    assert quarantine.quarantined[0].raw_timestamp == "2024-01-02T00:00:00Z"
