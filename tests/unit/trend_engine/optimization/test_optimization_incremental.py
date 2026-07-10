import pytest
from backend.trend_engine.optimization.repository.memory import InMemorySymbolTrendCache
from backend.trend_engine.optimization.engine.incremental import IncrementalProcessor
from backend.trend_engine.optimization.models.models import SymbolPipelineResult

@pytest.mark.asyncio
async def test_filter_candidates():
    cache = InMemorySymbolTrendCache()
    processor = IncrementalProcessor(cache)
    
    fingerprint = "hash123"
    
    # Save a cached result
    res1 = SymbolPipelineResult(
        symbol_key="AAPL:NASDAQ",
        detection_result={"fake": "d"},
        quality_result={"fake": "q"},
        lifecycle_result={"fake": "l"}
    )
    await cache.save_cached_result(fingerprint, res1)
    
    symbols = ["AAPL:NASDAQ", "MSFT:NASDAQ"]
    
    recompute, reused = await processor.filter_candidates(fingerprint, symbols)
    
    assert len(recompute) == 1
    assert recompute[0] == "MSFT:NASDAQ"
    
    assert len(reused) == 1
    assert "AAPL:NASDAQ" in reused
    assert reused["AAPL:NASDAQ"].symbol_key == "AAPL:NASDAQ"
