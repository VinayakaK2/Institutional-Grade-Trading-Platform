import pytest
from backend.universe_engine.optimization.models import (
    UniverseOptimizationConfiguration,
    OptimizedUniverse
)

@pytest.mark.asyncio
async def test_full_rebuild(test_engine, mock_classified_universe):
    """Tests optimization on an initial run (no previous optimized universe)."""
    result = await test_engine.generate_optimized_universe(
        run_id="run1",
        parent_classified_universe=mock_classified_universe,
        previous_optimized_universe=None
    )
    
    universe = result.universe
    assert universe.parent_classified_universe_id == mock_classified_universe.classified_universe_id
    assert universe.previous_optimized_universe_id is None
    assert universe.optimization_metrics.total_symbols == len(mock_classified_universe.classified_symbols)
    assert universe.optimization_metrics.symbols_reprocessed == len(mock_classified_universe.classified_symbols)
    assert universe.optimization_metrics.symbols_reused == 0
    assert len(universe.symbol_fingerprints) == 3

@pytest.mark.asyncio
async def test_partial_update_incremental(test_engine, mock_classified_universe):
    """Tests that unchanged symbols are correctly detected and bypassed."""
    # First run
    res1 = await test_engine.generate_optimized_universe(
        run_id="run1",
        parent_classified_universe=mock_classified_universe,
        previous_optimized_universe=None
    )
    
    # Second run with same data
    res2 = await test_engine.generate_optimized_universe(
        run_id="run2",
        parent_classified_universe=mock_classified_universe,
        previous_optimized_universe=res1.universe
    )
    
    universe2 = res2.universe
    assert universe2.previous_optimized_universe_id == res1.universe.optimized_universe_id
    assert universe2.optimization_metrics.total_symbols == 3
    assert universe2.optimization_metrics.symbols_reused == 3
    assert universe2.optimization_metrics.symbols_reprocessed == 0

@pytest.mark.asyncio
async def test_parallel_vs_sequential_equivalence(test_engine, mock_classified_universe):
    """Explicit deterministic regression test for Parallel vs Sequential."""
    
    # 1. Sequential execution
    test_engine._config.enable_parallel = False
    seq_res = await test_engine.generate_optimized_universe(
        run_id="seq_run",
        parent_classified_universe=mock_classified_universe
    )
    
    # 2. Parallel execution
    test_engine._config.enable_parallel = True
    par_res = await test_engine.generate_optimized_universe(
        run_id="par_run",
        parent_classified_universe=mock_classified_universe
    )
    
    seq_fps = seq_res.universe.symbol_fingerprints
    par_fps = par_res.universe.symbol_fingerprints
    
    # The output fingerprints MUST remain mathematically identical
    assert seq_fps == par_fps
    
    # The optimization engine must process all of them
    assert seq_res.universe.optimization_metrics.symbols_reprocessed == 3
    assert par_res.universe.optimization_metrics.symbols_reprocessed == 3
    
    # Parallel should register workers used
    assert par_res.universe.optimization_metrics.parallel_workers_used > 0

@pytest.mark.asyncio
async def test_feature_toggles_disable_all(test_engine, mock_classified_universe):
    """Tests that pipeline still works mathematically identically if all features disabled."""
    test_engine._config.enable_batching = False
    test_engine._config.enable_incremental = False
    test_engine._config.enable_parallel = False
    
    # Run once to get a previous snapshot
    res1 = await test_engine.generate_optimized_universe(
        run_id="run1",
        parent_classified_universe=mock_classified_universe
    )
    
    # Run again with same data, incremental is off so it should reprocess everything
    res2 = await test_engine.generate_optimized_universe(
        run_id="run2",
        parent_classified_universe=mock_classified_universe,
        previous_optimized_universe=res1.universe
    )
    
    # Since batching is disabled, batch count is exactly 3 (each item is its own batch)
    assert res2.universe.optimization_metrics.batch_count == 3
    # Incremental disabled, 0 reused
    assert res2.universe.optimization_metrics.symbols_reused == 0
    assert res2.universe.optimization_metrics.symbols_reprocessed == 3
    # Parallel disabled, 0 workers used
    assert res2.universe.optimization_metrics.parallel_workers_used == 0

@pytest.mark.asyncio
async def test_consecutive_incremental_executions(test_engine, mock_classified_universe):
    """
    Long-running regression test simulating multiple consecutive incremental executions.
    Sequence:
    1. Initial Snapshot (Full rebuild)
    2. 1 symbol changes
    3. No changes
    4. Multiple symbols change (simulated by updating all)
    5. Verifies equivalence to a direct complete rebuild
    """
    
    # 1. Initial Snapshot
    res_initial = await test_engine.generate_optimized_universe(
        run_id="run_initial",
        parent_classified_universe=mock_classified_universe,
        previous_optimized_universe=None
    )
    assert res_initial.universe.optimization_metrics.symbols_reprocessed == 3
    
    # 2. 1 symbol changes
    mutated_universe_1 = mock_classified_universe.model_copy(deep=True)
    mutated_universe_1.classified_symbols[0] = mutated_universe_1.classified_symbols[0].model_copy(update={"sector": "Mutated Sector"})
    
    res_mutated_1 = await test_engine.generate_optimized_universe(
        run_id="run_mutated_1",
        parent_classified_universe=mutated_universe_1,
        previous_optimized_universe=res_initial.universe
    )
    assert res_mutated_1.universe.optimization_metrics.symbols_reprocessed == 1
    assert res_mutated_1.universe.optimization_metrics.symbols_reused == 2
    
    # 3. No changes
    res_no_change = await test_engine.generate_optimized_universe(
        run_id="run_no_change",
        parent_classified_universe=mutated_universe_1,
        previous_optimized_universe=res_mutated_1.universe
    )
    assert res_no_change.universe.optimization_metrics.symbols_reprocessed == 0
    assert res_no_change.universe.optimization_metrics.symbols_reused == 3
    
    # 4. Multiple (All) symbols change
    mutated_universe_all = mutated_universe_1.model_copy(deep=True)
    for i in range(len(mutated_universe_all.classified_symbols)):
        mutated_universe_all.classified_symbols[i] = mutated_universe_all.classified_symbols[i].model_copy(update={"industry": "Mutated Industry"})
        
    res_mutated_all = await test_engine.generate_optimized_universe(
        run_id="run_mutated_all",
        parent_classified_universe=mutated_universe_all,
        previous_optimized_universe=res_no_change.universe
    )
    assert res_mutated_all.universe.optimization_metrics.symbols_reprocessed == 3
    assert res_mutated_all.universe.optimization_metrics.symbols_reused == 0
    
    # 5. Full rebuild of the final state
    res_full_rebuild = await test_engine.generate_optimized_universe(
        run_id="run_full_rebuild",
        parent_classified_universe=mutated_universe_all,
        previous_optimized_universe=None
    )
    
    # Verify that the final incremental state perfectly matches the full rebuild state
    assert res_mutated_all.universe.symbol_fingerprints == res_full_rebuild.universe.symbol_fingerprints
