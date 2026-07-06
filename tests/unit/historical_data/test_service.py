import pytest
import asyncio
from datetime import datetime
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.engine.manager import DownloadManager
from backend.historical_data.engine.pipeline import DownloadPipeline
from backend.historical_data.providers.manager import ProviderManager
from backend.historical_data.service import HistoricalDataService

class DummyStorage:
    async def save_raw_candles(self, candles): pass
    async def save_normalized_candles(self, candles): pass
    async def get_raw_candles(self, symbol, timeframe, start, end):
        if False: yield None
    async def save_metadata(self, metadata): pass

@pytest.fixture
def dummy_symbol():
    return SymbolReference(symbol="TEST", exchange=ExchangeReference(name="TEST", code="TEST"))

@pytest.fixture
def service():
    pipeline = DownloadPipeline(DummyStorage())
    p_manager = ProviderManager()
    manager = DownloadManager(p_manager, pipeline, max_concurrent=1)
    return HistoricalDataService(manager)

@pytest.mark.asyncio
async def test_historical_data_service(service, dummy_symbol):
    service.start_pipeline(workers=1)
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    req_id = await service.request_download(
        symbol=dummy_symbol,
        timeframe=Timeframe.D1,
        start_date=start,
        end_date=end,
        provider="mock"
    )
    
    assert req_id is not None
    status = service.get_download_status(req_id)
    assert status is not None
    assert status.symbol == dummy_symbol
    
    await service.stop_pipeline()
