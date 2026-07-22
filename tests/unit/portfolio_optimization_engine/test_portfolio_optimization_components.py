import pytest
from backend.portfolio_optimization_engine.rules.structural_rules import PortfolioOptimizationStructuralRules
from backend.portfolio_optimization_engine.rules.consistency_rules import PortfolioOptimizationConsistencyRules
from backend.portfolio_optimization_engine.pipeline.optimization_aggregation import PortfolioOptimizationAggregationStage
from backend.portfolio_optimization_engine.pipeline.optimization_metadata import PortfolioOptimizationMetadataStage


def test_structural_rules(mock_execution_context):
    rules = PortfolioOptimizationStructuralRules()
    rules.validate(mock_execution_context)

    mock_execution_context.portfolio_state_snapshot = None
    with pytest.raises(ValueError, match="Missing PortfolioStateSnapshot"):
        rules.validate(mock_execution_context)

def test_consistency_rules_valid(mock_execution_context):
    rules = PortfolioOptimizationConsistencyRules()
    rules.validate(mock_execution_context)

def test_consistency_rules_dataset_mismatch(mock_execution_context):
    rules = PortfolioOptimizationConsistencyRules()
    mock_execution_context.portfolio_state_snapshot.dataset_version = "v2"
    with pytest.raises(ValueError, match="Dataset version mismatch"):
        rules.validate(mock_execution_context)

def test_consistency_rules_lineage_mismatch(mock_execution_context):
    rules = PortfolioOptimizationConsistencyRules()
    mock_execution_context.portfolio_decision_snapshot.lineage.portfolio_state_snapshot.snapshot_id = "state_999"
    with pytest.raises(ValueError, match="Lineage mismatch"):
        rules.validate(mock_execution_context)

@pytest.mark.asyncio
async def test_aggregation_stage(pipeline_context):
    stage = PortfolioOptimizationAggregationStage()
    ctx = await stage.execute(pipeline_context)
    
    assert ctx.aggregated_facts["portfolio_state_id"] == "state_1"
    assert ctx.aggregated_facts["portfolio_exposure_id"] == "exp_1"
    assert ctx.aggregated_facts["portfolio_decision"] == "APPROVED"
    assert ctx.aggregated_facts["optimization_targets"] == {"target_weight": 0.05}

@pytest.mark.asyncio
async def test_metadata_stage(pipeline_context):
    stage1 = PortfolioOptimizationAggregationStage()
    stage2 = PortfolioOptimizationMetadataStage()
    
    ctx = await stage1.execute(pipeline_context)
    ctx = await stage2.execute(ctx)
    
    assert ctx.optimization_result is not None
    assert ctx.optimization_result.metadata["preparation_status"] == "READY_FOR_OPTIMIZATION"
    assert "portfolio_state_id" in ctx.optimization_result.metadata["aggregated_facts"]
