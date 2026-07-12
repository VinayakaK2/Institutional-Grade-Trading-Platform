import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.liquidity_grab_engine.optimization.engine.engine import LiquidityGrabOptimizationEngine
from backend.liquidity_grab_engine.optimization.repository.memory import InMemoryOptimizationRepository
from backend.liquidity_grab_engine.optimization.models.models import OptimizationContext
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LiquidityGrabLifecycleSnapshot,
    LifecycleSummary,
    LiquidityGrabLifecycleState,
    LifecycleEvidence
)

@pytest.fixture
def mock_lifecycle_engine():
    engine = MagicMock()
    # Mocking the async execute method
    async def mock_execute(ctx):
        return LiquidityGrabLifecycleSnapshot(
            snapshot_id=f"ls_{ctx.candidate.candidate_id}",
            candidate_id=ctx.candidate.candidate_id,
            symbol_id="sym1",
            timeframe="H1",
            evidence=LifecycleEvidence(),
            metadata={},
            summary=LifecycleSummary(state=LiquidityGrabLifecycleState.ACTIVE, aggregator_version="1.0.0")
        )
    engine.execute = mock_execute
    return engine

@pytest.fixture
def mock_context():
    # We just need it to have candidate.candidate_id, dataset_version, etc.
    ctx = MagicMock()
    ctx.candidate.candidate_id = "c1"
    ctx.candidate.dataset_version = 1
    ctx.candidate.configuration_hash = "h"
    ctx.candidate.metadata.pipeline_version = "v1"
    ctx.quality_report.metadata.pipeline_version = "v2"
    ctx.lifecycle_summary.aggregator_version = "1.0.0"
    return ctx

@pytest.mark.asyncio
async def test_engine_incremental_processing(mock_lifecycle_engine, mock_context):
    repo = InMemoryOptimizationRepository()
    opt_engine = LiquidityGrabOptimizationEngine(
        lifecycle_engine=mock_lifecycle_engine,
        repository=repo
    )
    
    # 1. First execution - cache miss
    ctx = OptimizationContext(cache_enabled=True, reuse_enabled=True)
    results_run1 = await opt_engine.execute_batch([mock_context], ctx)
    
    assert len(results_run1) == 1
    assert results_run1[0].runtime_statistics.cache_misses == 1
    assert results_run1[0].runtime_statistics.cache_hits == 0
    assert results_run1[0].runtime_statistics.candidates_processed == 1
    
    # 2. Second execution - cache hit
    results_run2 = await opt_engine.execute_batch([mock_context], ctx)
    
    assert len(results_run2) == 1
    assert results_run2[0].runtime_statistics.cache_misses == 0
    assert results_run2[0].runtime_statistics.cache_hits == 1
    # Check it actually returns the same snapshot structure
    assert results_run2[0].snapshot_id == results_run1[0].snapshot_id
    
@pytest.mark.asyncio
async def test_engine_cache_disabled(mock_lifecycle_engine, mock_context):
    repo = InMemoryOptimizationRepository()
    opt_engine = LiquidityGrabOptimizationEngine(
        lifecycle_engine=mock_lifecycle_engine,
        repository=repo
    )
    
    # Run once to populate cache (with cache enabled)
    await opt_engine.execute_batch([mock_context], OptimizationContext(cache_enabled=True, reuse_enabled=True))
    
    # Run again with cache_disabled
    ctx_disabled = OptimizationContext(cache_enabled=False, reuse_enabled=False)
    results = await opt_engine.execute_batch([mock_context], ctx_disabled)
    
    assert results[0].runtime_statistics.cache_misses == 1
    assert results[0].runtime_statistics.cache_hits == 0

@pytest.mark.asyncio
async def test_engine_merges_hits_and_misses(mock_lifecycle_engine):
    repo = InMemoryOptimizationRepository()
    opt_engine = LiquidityGrabOptimizationEngine(
        lifecycle_engine=mock_lifecycle_engine,
        repository=repo
    )
    
    ctx1 = MagicMock()
    ctx1.candidate.candidate_id = "c1"
    ctx1.candidate.dataset_version = 1
    ctx1.candidate.configuration_hash = "h"
    ctx1.candidate.metadata.pipeline_version = "v1"
    ctx1.quality_report.metadata.pipeline_version = "v2"
    ctx1.lifecycle_summary.aggregator_version = "1.0.0"
    
    ctx2 = MagicMock()
    ctx2.candidate.candidate_id = "c2"
    ctx2.candidate.dataset_version = 1
    ctx2.candidate.configuration_hash = "h"
    ctx2.candidate.metadata.pipeline_version = "v1"
    ctx2.quality_report.metadata.pipeline_version = "v2"
    ctx2.lifecycle_summary.aggregator_version = "1.0.0"
    
    # Pre-cache c1
    await opt_engine.execute_batch([ctx1], OptimizationContext())
    
    # Execute batch with both c1 (hit) and c2 (miss)
    results = await opt_engine.execute_batch([ctx1, ctx2], OptimizationContext())
    
    assert len(results) == 2
    
    # Output order should match input order (c1, c2)
    assert results[0].business_fingerprint.candidate_id == "c1"
    assert results[1].business_fingerprint.candidate_id == "c2"
    
    # Stats should reflect 1 hit, 1 miss on BOTH snapshot stats
    assert results[0].runtime_statistics.cache_hits == 1
    assert results[0].runtime_statistics.cache_misses == 1
    assert results[1].runtime_statistics.cache_hits == 1
    assert results[1].runtime_statistics.cache_misses == 1
