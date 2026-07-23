import pytest
from backend.paper_execution_optimization_engine.cache.memory_cache import MemoryCacheStore
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot, OptimizationRuntimeStatistics

@pytest.fixture
def sample_snapshot():
    return PaperExecutionOptimizationSnapshot(
        optimization_fingerprint="fp1",
        business_fingerprint="biz1",
        canonical_hash="hash1",
        snapshot_version="snap1",
        optimization_summary=OptimizationRuntimeStatistics(),
        metadata={}
    )

@pytest.mark.asyncio
async def test_memory_cache_resolve_miss(sample_snapshot):
    cache = MemoryCacheStore()
    
    called = False
    async def factory():
        nonlocal called
        called = True
        return sample_snapshot
        
    result = await cache.resolve("fp1", factory)
    
    assert called is True
    assert result == sample_snapshot
    assert await cache.load("fp1") == sample_snapshot

@pytest.mark.asyncio
async def test_memory_cache_resolve_hit(sample_snapshot):
    cache = MemoryCacheStore()
    await cache.save(sample_snapshot)
    
    called = False
    async def factory():
        nonlocal called
        called = True
        return sample_snapshot
        
    result = await cache.resolve("fp1", factory)
    
    assert called is False
    assert result == sample_snapshot

@pytest.mark.asyncio
async def test_memory_cache_invalidate(sample_snapshot):
    cache = MemoryCacheStore()
    await cache.save(sample_snapshot)
    
    await cache.invalidate("fp1")
    
    with pytest.raises(KeyError):
        await cache.load("fp1")
