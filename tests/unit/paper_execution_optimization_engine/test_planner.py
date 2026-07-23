import pytest
from backend.paper_execution_optimization_engine.engine.execution_reuse_planner import ExecutionReusePlanner
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.config.config import OptimizationConfig
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultExecutionContext

@pytest.fixture
def base_context():
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
        optimization_configuration=OptimizationConfig(caching_enabled=True, configuration_hash="opt_1"),
        optimization_metadata={}
    )

def test_planner_identifies_reusable(base_context):
    planner = ExecutionReusePlanner(
        current_dataset_version="ds_v1",
        current_pipeline_version="pipe_1",
        current_optimization_config_hash="opt_1"
    )
    
    planned = planner.plan_batch([base_context])
    
    assert len(planned) == 1
    _, _, is_reusable = planned[0]
    
    assert is_reusable is True

def test_planner_invalidates_on_dataset_change(base_context):
    # Current dataset is ds_v2, but the context was built with ds_v1
    planner = ExecutionReusePlanner(
        current_dataset_version="ds_v2",
        current_pipeline_version="pipe_1",
        current_optimization_config_hash="opt_1"
    )
    
    planned = planner.plan_batch([base_context])
    
    assert len(planned) == 1
    _, _, is_reusable = planned[0]
    
    assert is_reusable is False
