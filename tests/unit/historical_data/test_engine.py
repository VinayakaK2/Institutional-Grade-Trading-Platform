import pytest
import asyncio
from datetime import datetime
from backend.historical_data.engine.pipeline import DownloadPipeline
from backend.historical_data.engine.manager import DownloadManager
from backend.historical_data.providers.manager import ProviderManager
from backend.historical_data.providers.mock_provider import MockHistoricalProvider
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.models.metadata import DownloadRequest, DownloadStatus

class DummyStorage:
    def __init__(self):
        self.raw_saved = 0
        self.norm_saved = 0
    async def save_raw_candles(self, candles):
        self.raw_saved += len(candles)
        
    async def save_normalized_candles(self, candles):
        self.norm_saved += len(candles)
        
    async def get_raw_candles(self, symbol, timeframe, start, end):
        # mock empty generator
        if False:
            yield None
            
    async def save_metadata(self, metadata):
        pass

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="MSFT", exchange=ExchangeReference(name="NASDAQ", code="NASDAQ"))

@pytest.mark.asyncio
async def test_download_manager_success(dummy_symbol):
    storage = DummyStorage()
    pipeline = DownloadPipeline(storage, batch_size=2)
    
    p_manager = ProviderManager()
    p_manager.register_provider(MockHistoricalProvider("mock", healthy=True))
    
    dl_manager = DownloadManager(p_manager, pipeline, max_concurrent=2)
    dl_manager.start(worker_count=1)
    
    req = DownloadRequest(
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 5) # 5 days
    )
    
    req_id = await dl_manager.enqueue(req)
    
    # Wait for completion
    await asyncio.sleep(0.1)
    
    status = dl_manager.get_status(req_id)
    assert status.status == DownloadStatus.COMPLETED
    assert status.records_saved == 5
    assert storage.raw_saved == 5
    assert storage.norm_saved == 5

@pytest.mark.asyncio
async def test_download_pipeline_replay(dummy_symbol):
    class ReplayStorage(DummyStorage):
        async def get_raw_candles(self, symbol, timeframe, start, end):
            from backend.historical_data.models.raw import RawCandle
            yield RawCandle(
                provider="mock",
                symbol=symbol,
                timeframe=timeframe,
                raw_timestamp="2024-01-01T00:00:00Z",
                raw_open=100.0,
                raw_high=105.0,
                raw_low=95.0,
                raw_close=102.0,
                raw_volume=1000.0
            )
            
    storage = ReplayStorage()
    pipeline = DownloadPipeline(storage, batch_size=2)
    
    count = await pipeline.replay_raw_data(
        dummy_symbol, 
        Timeframe.D1, 
        datetime(2024,1,1), 
        datetime(2024,1,2)
    )
    
    assert count == 1
    assert storage.norm_saved == 1
    assert storage.raw_saved == 0

@pytest.mark.asyncio
async def test_download_manager_rate_limit(dummy_symbol):
    from backend.historical_data.providers.base import BaseHistoricalProvider
    class RateLimitProvider(BaseHistoricalProvider):
        def _get_provider_id(self): return "rate_limiter"
        async def fetch_candles(self, symbol, timeframe, start, end):
            from backend.historical_data.exceptions import RateLimitException
            raise RateLimitException("rate_limiter", 0)

    class RateLimitManager(ProviderManager):
        def get_provider(self, name): return RateLimitProvider()

    storage = DummyStorage()
    pipeline = DownloadPipeline(storage)
    dl_manager = DownloadManager(RateLimitManager(), pipeline)
    dl_manager.start(worker_count=1)
    
    req = DownloadRequest(
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 5),
        provider="mock"
    )
    
    req_id = await dl_manager.enqueue(req)
    
    import asyncio
    await asyncio.sleep(0.1) # allow worker to process and fail
    
    status = dl_manager.get_status(req_id)
    assert status.status == DownloadStatus.FAILED
    
    await dl_manager.stop()

def test_download_manager_invalid_request():
    storage = DummyStorage()
    pipeline = DownloadPipeline(storage)
    dl_manager = DownloadManager(ProviderManager(), pipeline)
    
    status = dl_manager.get_status("invalid_id")
    assert status is None
