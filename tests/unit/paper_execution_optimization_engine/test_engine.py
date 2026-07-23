import pytest
from backend.paper_execution_optimization_engine.engine.engine import PaperExecutionOptimizationEngine
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.config.config import OptimizationConfig
from backend.paper_execution_optimization_engine.cache.memory_cache import MemoryCacheStore
from backend.paper_execution_optimization_engine.repository.memory_repo import MemoryPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.executor.async_batch_executor import SyncExecutor
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot

class MockBusinessRepo:
    def __init__(self):
        self.store = {}
    def save(self, snap):
        self.store[snap.snapshot_version] = snap
    def load(self, snap_version):
        if snap_version not in self.store:
            raise KeyError()
        return self.store[snap_version]

class MockResultEngine:
    def execute(self, ctx):
        # We simulate creating a PaperExecutionSnapshot
        return PaperExecutionSnapshot.model_construct(
            snapshot_version=f"snap_{ctx.paper_order_snapshot.business_fingerprint}",
            parent_fill_snapshot_version="f1",
            parent_order_snapshot_version="o1",
            pipeline_version="1.0.0",
            business_fingerprint=f"biz_{ctx.paper_order_snapshot.business_fingerprint}",
            canonical_hash="hash_123",
            final_status="FILLED",
            metadata={}
        )

@pytest.fixture
def base_context():
    class MockSnapshot:
        def __init__(self, fp):
            self.business_fingerprint = fp
            
    exec_ctx = PaperExecutionResultExecutionContext.model_construct(
        dataset_version="ds_v1",
        configuration_hash="hash",
        portfolio_decision_snapshot=MockSnapshot("pds"),
        paper_order_snapshot=MockSnapshot("order_fp_1"),
        paper_fill_snapshot=MockSnapshot("fill_fp_1"),
        paper_execution_quality_snapshot=MockSnapshot("peqs")
    )
    
    return PaperExecutionOptimizationContext(
        execution_context=exec_ctx,
        optimization_configuration=OptimizationConfig(caching_enabled=True, configuration_hash="hash"),
        optimization_metadata={}
    )

@pytest.mark.asyncio
async def test_engine_successful_optimization_and_cache_miss(base_context):
    result_engine = MockResultEngine()
    biz_repo = MockBusinessRepo()
    executor = SyncExecutor()
    cache = MemoryCacheStore()
    opt_repo = MemoryPaperExecutionOptimizationRepository()
    
    engine = PaperExecutionOptimizationEngine(
        result_engine=result_engine, # type: ignore
        business_repository=biz_repo, # type: ignore
        executor=executor,
        cache=cache,
        repository=opt_repo
    )
    
    results = await engine.execute_batch([base_context], "ds_v1", "1.0.0", "hash")
    
    assert len(results) == 1
    opt_snap, biz_snap = results[0]
    
    assert opt_snap.optimization_summary.cache_misses == 1
    assert opt_snap.optimization_summary.cache_hits == 0
    assert opt_snap.optimization_summary.recomputed_snapshots == 1
    assert biz_snap.business_fingerprint == "biz_order_fp_1"
    
    # Assert persisted in cache and repos
    cached_snap = await cache.load(opt_snap.optimization_fingerprint)
    assert cached_snap.optimization_fingerprint == opt_snap.optimization_fingerprint
    assert cached_snap.is_business_equivalent(opt_snap)
    repo_snap = await opt_repo.load(opt_snap.optimization_fingerprint)
    assert repo_snap.optimization_fingerprint == opt_snap.optimization_fingerprint
    assert repo_snap.is_business_equivalent(opt_snap)
    assert biz_repo.load(opt_snap.snapshot_version) == biz_snap

@pytest.mark.asyncio
async def test_engine_successful_optimization_and_cache_hit(base_context):
    result_engine = MockResultEngine()
    biz_repo = MockBusinessRepo()
    executor = SyncExecutor()
    cache = MemoryCacheStore()
    opt_repo = MemoryPaperExecutionOptimizationRepository()
    
    engine = PaperExecutionOptimizationEngine(
        result_engine=result_engine, # type: ignore
        business_repository=biz_repo, # type: ignore
        executor=executor,
        cache=cache,
        repository=opt_repo
    )
    
    # First execution (miss)
    results1 = await engine.execute_batch([base_context], "ds_v1", "1.0.0", "hash")
    opt_snap1, _ = results1[0]
    
    # Second execution (hit)
    results2 = await engine.execute_batch([base_context], "ds_v1", "1.0.0", "hash")
    opt_snap2, biz_snap2 = results2[0]
    
    assert opt_snap2.optimization_summary.cache_hits == 1
    assert opt_snap2.optimization_summary.cache_misses == 0
    assert opt_snap2.optimization_summary.reused_snapshots == 1
    
    # Business fingerprint remains identical
    assert opt_snap1.is_business_equivalent(opt_snap2)

@pytest.mark.asyncio
async def test_engine_incremental_optimization():
    result_engine = MockResultEngine()
    biz_repo = MockBusinessRepo()
    executor = SyncExecutor()
    cache = MemoryCacheStore()
    opt_repo = MemoryPaperExecutionOptimizationRepository()
    
    engine = PaperExecutionOptimizationEngine(
        result_engine=result_engine, # type: ignore
        business_repository=biz_repo, # type: ignore
        executor=executor,
        cache=cache,
        repository=opt_repo
    )
    
    class MockSnapshot:
        def __init__(self, fp):
            self.business_fingerprint = fp
            
    ctx1 = PaperExecutionOptimizationContext(
        execution_context=PaperExecutionResultExecutionContext.model_construct(
            dataset_version="ds_v1",
            configuration_hash="hash",
            portfolio_decision_snapshot=MockSnapshot("pds"),
            paper_order_snapshot=MockSnapshot("order_fp_1"),
            paper_fill_snapshot=MockSnapshot("fill_fp_1"),
            paper_execution_quality_snapshot=MockSnapshot("peqs")
        ),
        optimization_configuration=OptimizationConfig(caching_enabled=True, configuration_hash="hash"),
        optimization_metadata={}
    )
    
    ctx2 = PaperExecutionOptimizationContext(
        execution_context=PaperExecutionResultExecutionContext.model_construct(
            dataset_version="ds_v1",
            configuration_hash="hash",
            portfolio_decision_snapshot=MockSnapshot("pds"),
            paper_order_snapshot=MockSnapshot("order_fp_2"),
            paper_fill_snapshot=MockSnapshot("fill_fp_2"),
            paper_execution_quality_snapshot=MockSnapshot("peqs")
        ),
        optimization_configuration=OptimizationConfig(caching_enabled=True, configuration_hash="hash"),
        optimization_metadata={}
    )
    
    # Run ctx1
    await engine.execute_batch([ctx1], "ds_v1", "1.0.0", "hash")
    
    # Run ctx1 and ctx2 in batch (incremental: ctx1 hit, ctx2 miss)
    results = await engine.execute_batch([ctx1, ctx2], "ds_v1", "1.0.0", "hash")
    
    assert len(results) == 2
    
    opt_snap1, biz_snap1 = results[0]
    opt_snap2, biz_snap2 = results[1]
    
    assert opt_snap1.optimization_summary.cache_hits == 1
    assert opt_snap1.optimization_summary.cache_misses == 1
    assert opt_snap2.optimization_summary.cache_hits == 1
    
    assert biz_snap1.business_fingerprint == "biz_order_fp_1"
    assert biz_snap2.business_fingerprint == "biz_order_fp_2"

@pytest.mark.asyncio
async def test_engine_cache_corruption_rejection(base_context):
    result_engine = MockResultEngine()
    biz_repo = MockBusinessRepo()
    executor = SyncExecutor()
    cache = MemoryCacheStore()
    opt_repo = MemoryPaperExecutionOptimizationRepository()
    
    engine = PaperExecutionOptimizationEngine(
        result_engine=result_engine, # type: ignore
        business_repository=biz_repo, # type: ignore
        executor=executor,
        cache=cache,
        repository=opt_repo
    )
    
    # Run to populate cache
    _ = await engine.execute_batch([base_context], "ds_v1", "1.0.0", "hash")
    
    # Manually corrupt cache by altering the fingerprint it returns
    from backend.paper_execution_optimization_engine.engine.fingerprint_builder import OptimizationFingerprintBuilder
    from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot, OptimizationRuntimeStatistics
    
    actual_fp = OptimizationFingerprintBuilder.build(base_context)
    
    corrupt_snap = PaperExecutionOptimizationSnapshot(
        optimization_fingerprint="CORRUPTED_FP",
        business_fingerprint="biz",
        canonical_hash="hash",
        snapshot_version="snap",
        optimization_summary=OptimizationRuntimeStatistics(),
        metadata={}
    )
    
    # Override in cache under the correct key, but payload has different fingerprint
    cache._store[actual_fp] = corrupt_snap
    
    # Second execution - should reject the cache because loaded_fp != expected_fp
    results2 = await engine.execute_batch([base_context], "ds_v1", "1.0.0", "hash")
    opt_snap2, _ = results2[0]
    
    assert opt_snap2.optimization_summary.cache_misses == 1
    assert opt_snap2.optimization_summary.cache_hits == 0
