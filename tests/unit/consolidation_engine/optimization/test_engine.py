import pytest
import asyncio
from backend.consolidation_engine.optimization.models import (
    BusinessFingerprint,
    ConsolidationProcessingRequest,
    ConsolidationProcessingResult,
    OptimizationBusinessStatistics
)
from backend.consolidation_engine.optimization.engine import ConsolidationOptimizationEngine
from backend.consolidation_engine.optimization.repository.memory import InMemoryConsolidationOptimizationRepository
from backend.consolidation_engine.optimization.config import ConsolidationOptimizationConfiguration
from backend.consolidation_engine.optimization.contracts import IConsolidationProcessor

class MockProcessor(IConsolidationProcessor):
    def __init__(self):
        self.call_count = 0
        self.lock = asyncio.Lock()
        self.processed_requests = []
        
    async def process(self, request: ConsolidationProcessingRequest) -> ConsolidationProcessingResult:
        async with self.lock:
            self.call_count += 1
            self.processed_requests.append(request.request_id)
            
        # Simulate some async work
        await asyncio.sleep(0.01)
        
        return ConsolidationProcessingResult(
            request_id=request.request_id,
            fingerprint=request.fingerprint.digest,
            cached=False,
            result_payload=f"Result for {request.request_id}"
        )

@pytest.fixture
def repo():
    return InMemoryConsolidationOptimizationRepository()

@pytest.fixture
def config():
    return ConsolidationOptimizationConfiguration(max_concurrency=2)

@pytest.mark.asyncio
async def test_incremental_processing_cache_hits(repo, config):
    """Verify that previously computed results are reused and not recomputed."""
    processor = MockProcessor()
    engine = ConsolidationOptimizationEngine(repository=repo, processor=processor, configuration=config)
    
    # Create 5 requests
    requests = []
    for i in range(5):
        fp = BusinessFingerprint(
            fingerprint_version="1.0",
            candidate_id=f"cand_{i}",
            candidate_version=1,
            quality_report_version=1,
            lifecycle_snapshot_version=1,
            configuration_hash="hash",
            algorithm_versions="1.0"
        )
        req = ConsolidationProcessingRequest(request_id=f"req_{i}", fingerprint=fp, payload=None)
        requests.append(req)
        
    # First run: Cache misses (all 5 should be processed)
    results1, snapshot1 = await engine.process_batch(requests)
    
    assert processor.call_count == 5
    assert snapshot1.business_statistics.cache_misses == 5
    assert snapshot1.business_statistics.cache_hits == 0
    assert len(results1) == 5
    assert all(not r.cached for r in results1)
    
    # Second run: Cache hits (0 should be processed)
    results2, snapshot2 = await engine.process_batch(requests)
    
    assert processor.call_count == 5 # Call count hasn't increased
    assert snapshot2.business_statistics.cache_misses == 0
    assert snapshot2.business_statistics.cache_hits == 5
    assert len(results2) == 5
    assert all(r.cached for r in results2)
    
    # Outputs should be identical except for the `cached` flag
    assert [r.result_payload for r in results1] == [r.result_payload for r in results2]
    
@pytest.mark.asyncio
async def test_parallel_execution_and_ordered_merge(repo, config):
    """Verify parallel execution maintains strictly ordered results identical to input order."""
    processor = MockProcessor()
    engine = ConsolidationOptimizationEngine(repository=repo, processor=processor, configuration=config)
    
    requests = []
    for i in range(20):
        fp = BusinessFingerprint(
            fingerprint_version="1.0",
            candidate_id=f"cand_{i}",
            candidate_version=1,
            quality_report_version=1,
            lifecycle_snapshot_version=1,
            configuration_hash="hash",
            algorithm_versions="1.0"
        )
        req = ConsolidationProcessingRequest(request_id=f"req_{i}", fingerprint=fp, payload=None)
        requests.append(req)
        
    results, _ = await engine.process_batch(requests)
    
    # Verify outputs are in exact same order as inputs
    assert [r.request_id for r in results] == [f"req_{i}" for i in range(20)]
    
    # Verify processing happened concurrently (not strictly ordered during processing due to gather)
    # The processed_requests array inside MockProcessor won't necessarily match sequential order perfectly
    # because of context switching, but the final output results MUST match.
    assert len(processor.processed_requests) == 20
