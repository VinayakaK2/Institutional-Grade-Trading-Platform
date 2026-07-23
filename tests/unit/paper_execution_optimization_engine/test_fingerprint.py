import pytest
from backend.paper_execution_optimization_engine.engine.fingerprint_builder import OptimizationFingerprintBuilder
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.config.config import OptimizationConfig
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext

@pytest.fixture
def base_context():
    # Mocking or instantiating real snapshots might be hard, but let's assume we can mock their properties
    class MockSnapshot:
        def __init__(self, fp):
            self.business_fingerprint = fp
            
    exec_ctx = PaperExecutionResultExecutionContext.model_construct(
        dataset_version="ds_v1",
        order_snapshot=MockSnapshot("order_fp_1"),
        fill_snapshot=MockSnapshot("fill_fp_1"),
        configuration_hash="hash",
        portfolio_decision_snapshot=MockSnapshot("pds"),
        paper_order_snapshot=MockSnapshot("pos"),
        paper_fill_snapshot=MockSnapshot("pfs"),
        paper_execution_quality_snapshot=MockSnapshot("peqs")
    )
    
    return PaperExecutionOptimizationContext(
        execution_context=exec_ctx,
        optimization_configuration=OptimizationConfig(caching_enabled=True),
        optimization_metadata={}
    )

def test_fingerprint_deterministic(base_context):
    fp1 = OptimizationFingerprintBuilder.build(base_context)
    fp2 = OptimizationFingerprintBuilder.build(base_context)
    
    assert fp1 == fp2

def test_fingerprint_changes_on_dataset_version(base_context):
    fp1 = OptimizationFingerprintBuilder.build(base_context)
    
    class MockSnapshot:
        def __init__(self, fp):
            self.business_fingerprint = fp
            
    exec_ctx = PaperExecutionResultExecutionContext.model_construct(
        dataset_version="ds_v2",
        order_snapshot=MockSnapshot("order_fp_1"),
        fill_snapshot=MockSnapshot("fill_fp_1"),
        configuration_hash="hash",
        portfolio_decision_snapshot=MockSnapshot("pds"),
        paper_order_snapshot=MockSnapshot("pos"),
        paper_fill_snapshot=MockSnapshot("pfs"),
        paper_execution_quality_snapshot=MockSnapshot("peqs")
    )
    
    new_context = PaperExecutionOptimizationContext(
        execution_context=exec_ctx,
        optimization_configuration=OptimizationConfig(caching_enabled=True),
        optimization_metadata={}
    )
    
    fp2 = OptimizationFingerprintBuilder.build(new_context)
    
    assert fp1 != fp2

def test_fingerprint_changes_on_cache_config(base_context):
    fp1 = OptimizationFingerprintBuilder.build(base_context)
    
    new_context = PaperExecutionOptimizationContext(
        execution_context=base_context.execution_context,
        optimization_configuration=OptimizationConfig(caching_enabled=False),
        optimization_metadata={}
    )
    
    fp2 = OptimizationFingerprintBuilder.build(new_context)
    
    assert fp1 != fp2
