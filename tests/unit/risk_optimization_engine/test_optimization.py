import pytest
import asyncio
from typing import Any
from backend.risk_optimization_engine.models.fingerprint import BusinessFingerprint
from backend.risk_optimization_engine.models.request import OptimizationRequest
from backend.risk_optimization_engine.contracts.pipeline import IRiskPipeline
from backend.risk_optimization_engine.core.engine import RiskOptimizationEngine
from backend.risk_optimization_engine.core.executor import AsyncBatchExecutor
from backend.risk_optimization_engine.core.statistics import StatisticsCollector
from backend.risk_optimization_engine.cache.memory import MemoryCacheStore
from backend.risk_optimization_engine.metrics.memory import MemoryMetricsRepository
from backend.risk_optimization_engine.core.generator import FingerprintGenerator

class MockPipeline(IRiskPipeline):
    def __init__(self, delay: float = 0.01, fail_on: list = None):
        self.delay = delay
        self.fail_on = fail_on or []
        self.call_count = 0
        
    async def execute(self, request: OptimizationRequest) -> Any:
        self.call_count += 1
        if self.call_count in self.fail_on:
            raise asyncio.TimeoutError("Mock transient worker failure")
        await asyncio.sleep(self.delay)
        return {"result": f"processed_{request.raw_input}", "fingerprint": request.fingerprint.fingerprint_hash}

def create_mock_request(raw_input: int) -> OptimizationRequest:
    fp_hash = FingerprintGenerator.generate_fingerprint_hash(
        dataset_version="v1",
        algorithm_versions={},
        rule_versions={},
        strategy_version="s1",
        parent_snapshot_id=f"parent_{raw_input}",
        risk_percentage=1.0,
        position_sizing_config={},
        portfolio_config={},
        decision_config={}
    )
    fp = BusinessFingerprint(
        fingerprint_hash=fp_hash,
        dataset_version="v1",
        algorithm_versions={},
        rule_versions={},
        strategy_version="s1",
        parent_snapshot_id=f"parent_{raw_input}",
        risk_percentage=1.0,
        position_sizing_config={},
        portfolio_config={},
        decision_config={}
    )
    return OptimizationRequest(pipeline_version="1.0", fingerprint=fp, raw_input=raw_input)

@pytest.mark.asyncio
async def test_all_cache_misses():
    cache = MemoryCacheStore()
    metrics = MemoryMetricsRepository()
    stats = StatisticsCollector(metrics)
    executor = AsyncBatchExecutor(max_workers=5, batch_size=10)
    pipeline = MockPipeline()
    
    engine = RiskOptimizationEngine(cache, pipeline, stats, executor)
    
    requests = [create_mock_request(i) for i in range(20)]
    results = await engine.execute_batch(requests)
    
    assert len(results) == 20
    assert pipeline.call_count == 20
    assert results[0]["result"] == "processed_0"
    assert results[19]["result"] == "processed_19"
    
    saved_stats = await metrics.get_all_statistics()
    assert len(saved_stats) == 1
    assert saved_stats[0].cache_misses == 20
    assert saved_stats[0].cache_hits == 0

@pytest.mark.asyncio
async def test_all_cache_hits():
    cache = MemoryCacheStore()
    metrics = MemoryMetricsRepository()
    stats = StatisticsCollector(metrics)
    executor = AsyncBatchExecutor(max_workers=5, batch_size=10)
    pipeline = MockPipeline()
    
    engine = RiskOptimizationEngine(cache, pipeline, stats, executor)
    
    requests = [create_mock_request(i) for i in range(20)]
    
    # Pre-populate cache
    for req in requests:
        key = FingerprintGenerator.generate_cache_key(req)
        await cache.save(key, {"result": f"processed_{req.raw_input}", "fingerprint": req.fingerprint.fingerprint_hash})
        
    results = await engine.execute_batch(requests)
    
    assert len(results) == 20
    assert pipeline.call_count == 0 # None executed
    
    saved_stats = await metrics.get_all_statistics()
    assert saved_stats[0].cache_hits == 20
    assert saved_stats[0].cache_misses == 0

@pytest.mark.asyncio
async def test_stress_mixed():
    cache = MemoryCacheStore()
    metrics = MemoryMetricsRepository()
    stats = StatisticsCollector(metrics)
    executor = AsyncBatchExecutor(max_workers=50, batch_size=100)
    pipeline = MockPipeline(delay=0.001)
    
    engine = RiskOptimizationEngine(cache, pipeline, stats, executor)
    
    requests = [create_mock_request(i) for i in range(1000)]
    
    # Pre-populate half the cache
    for req in requests[:500]:
        key = FingerprintGenerator.generate_cache_key(req)
        await cache.save(key, {"result": f"processed_{req.raw_input}", "fingerprint": req.fingerprint.fingerprint_hash})
        
    results = await engine.execute_batch(requests)
    
    assert len(results) == 1000
    assert pipeline.call_count == 500
    
    saved_stats = await metrics.get_all_statistics()
    assert saved_stats[0].cache_hits == 500
    assert saved_stats[0].cache_misses == 500
    assert saved_stats[0].total_snapshots == 1000

@pytest.mark.asyncio
async def test_worker_failure_with_retry():
    cache = MemoryCacheStore()
    metrics = MemoryMetricsRepository()
    stats = StatisticsCollector(metrics)
    executor = AsyncBatchExecutor(max_workers=2, batch_size=2, retry=1)
    pipeline = MockPipeline(fail_on=[1]) # Fail on first call
    
    engine = RiskOptimizationEngine(cache, pipeline, stats, executor)
    requests = [create_mock_request(1)]
    
    results = await engine.execute_batch(requests)
    
    assert len(results) == 1
    assert pipeline.call_count == 2 # 1 fail + 1 retry

@pytest.mark.asyncio
async def test_timeout():
    executor = AsyncBatchExecutor(max_workers=2, batch_size=2, timeout=0.01)
    pipeline = MockPipeline(delay=0.1) # Pipeline is slow
    cache = MemoryCacheStore()
    stats = StatisticsCollector(MemoryMetricsRepository())
    engine = RiskOptimizationEngine(cache, pipeline, stats, executor)
    
    requests = [create_mock_request(1)]
    with pytest.raises(asyncio.TimeoutError):
        await engine.execute_batch(requests)
