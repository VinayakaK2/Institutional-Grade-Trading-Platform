import pytest
import asyncio
from backend.universe_engine.optimization.stages import (
    compute_business_fingerprint,
    DiffDetectionStage,
    BatchBuilderStage,
    ParallelExecutorStage,
    ReuseUnchangedSymbolsStage
)
from backend.universe_engine.optimization.models import UniverseOptimizationContext, UniverseOptimizationConfiguration
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_compute_business_fingerprint(mock_classified_symbols):
    sym = mock_classified_symbols[0]
    fp1 = compute_business_fingerprint(sym)
    fp2 = compute_business_fingerprint(sym)
    assert fp1 == fp2
    
    # Change business logic
    sym_mutated = mock_classified_symbols[0].model_copy(update={"sector": "Different"})
    fp3 = compute_business_fingerprint(sym_mutated)
    assert fp1 != fp3

@pytest.mark.asyncio
async def test_diff_detection_stage(mock_classified_symbols):
    config = UniverseOptimizationConfiguration(enable_incremental=True)
    context = UniverseOptimizationContext(
        run_id="run1",
        parent_classified_universe_id="parent1",
        config=config,
        started_at=datetime.now(timezone.utc)
    )
    
    # First run: no previous fingerprints
    stage = DiffDetectionStage(previous_fingerprints={})
    
    async def stream(items):
        for item in items:
            yield item
            
    tasks = [t async for t in stage.execute(context, stream(mock_classified_symbols))]
    assert len(tasks) == 3
    assert all(t.is_changed for t in tasks)
    assert context.metrics.symbols_reprocessed == 3
    assert context.metrics.symbols_reused == 0
    
    # Second run: all unchanged
    prev_fps = {t.symbol.symbol.symbol.symbol: t.fingerprint for t in tasks}
    context.metrics.symbols_reprocessed = 0
    
    stage2 = DiffDetectionStage(previous_fingerprints=prev_fps)
    tasks2 = [t async for t in stage2.execute(context, stream(mock_classified_symbols))]
    assert len(tasks2) == 3
    assert not any(t.is_changed for t in tasks2)
    assert context.metrics.symbols_reused == 3
    assert context.metrics.symbols_reprocessed == 0

@pytest.mark.asyncio
async def test_batch_builder_stage(mock_classified_symbols):
    config = UniverseOptimizationConfiguration(enable_batching=True, batch_size=2)
    context = UniverseOptimizationContext(
        run_id="run1",
        parent_classified_universe_id="parent1",
        config=config,
        started_at=datetime.now(timezone.utc)
    )
    
    stage = DiffDetectionStage()
    async def stream(items):
        for item in items:
            yield item
            
    tasks = [t async for t in stage.execute(context, stream(mock_classified_symbols))]
    
    batch_stage = BatchBuilderStage()
    async def task_stream(tasks):
        for t in tasks:
            yield t
            
    batches = [b async for b in batch_stage.execute(context, task_stream(tasks))]
    # 3 symbols, batch size 2 -> 2 batches
    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert len(batches[1]) == 1
    assert context.metrics.batch_count == 2
