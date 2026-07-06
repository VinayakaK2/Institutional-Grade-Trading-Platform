import pytest
from backend.historical_data.engine.manager import DownloadManager
from backend.historical_data.engine.pipeline import DownloadPipeline
from backend.historical_data.models.metadata import DownloadMetadata, DownloadStatus
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from datetime import datetime

class DummyStorage:
    async def save_metadata(self, meta): pass

class DummyProviderManager:
    pass

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ"))

@pytest.mark.asyncio
async def test_download_manager_execute_retry(dummy_symbol):
    pipeline = DownloadPipeline(DummyStorage())
    from backend.historical_data.exceptions import RateLimitException
    class FailingProvider:
        name = "mock"
        def get_historical_data(self, *args, **kwargs):
            raise RateLimitException("mock", 0.01)
            
    class RateLimitProviderManager:
        def get_provider(self, name):
            return FailingProvider()
            
    dl_manager = DownloadManager(RateLimitProviderManager(), pipeline)
    
    from backend.historical_data.engine.manager import DownloadRequest
    req = DownloadRequest(
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,1,2),
        provider="mock"
    )
    
    dl_manager._state["req1"] = DownloadMetadata(
        request_id="req1",
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,1,2),
        provider="mock"
    )
    await dl_manager._process_request(req, "req1")
    
    # It should have failed and retried, but in _process_request it just returns without raising
    status = dl_manager.get_status("req1")
    assert status.status == DownloadStatus.FAILED
