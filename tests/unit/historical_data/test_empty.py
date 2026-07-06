import pytest
from backend.historical_data.storage.postgres import PostgreSQLHistoricalStorage

@pytest.mark.asyncio
async def test_postgres_empty():
    storage = PostgreSQLHistoricalStorage(None)
    await storage.save_raw_candles([])
    await storage.save_normalized_candles([])

def test_pipeline_empty():
    from backend.historical_data.engine.pipeline import DownloadPipeline
    from backend.historical_data.models.raw import RawCandle
    
    class DummyStorage:
        pass
        
    pipeline = DownloadPipeline(DummyStorage())
    # we don't need to await because it returns immediately? Wait, they are async.
    
@pytest.mark.asyncio
async def test_pipeline_empty_async():
    from backend.historical_data.engine.pipeline import DownloadPipeline
    class DummyStorage:
        async def save_raw_candles(self, candles): pass
        async def save_normalized_candles(self, candles): pass
    pipeline = DownloadPipeline(DummyStorage())
    
    async def empty_stream():
        if False:
            yield None
            
    await pipeline.process_stream(empty_stream())
