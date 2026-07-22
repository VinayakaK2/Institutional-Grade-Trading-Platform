import pytest
from unittest.mock import MagicMock
from backend.portfolio_decision_engine.models.decision_models import DecisionStatus
from backend.portfolio_decision_engine.rules.structural_rules import PortfolioDecisionStructuralRules
from backend.portfolio_decision_engine.rules.consistency_rules import PortfolioDecisionConsistencyRules
from backend.portfolio_decision_engine.pipeline.decision_aggregation import DecisionAggregationStage
from backend.portfolio_decision_engine.pipeline.decision_rules import DecisionRulesStage
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionPipelineContext, PortfolioDecisionExecutionContext
from backend.portfolio_decision_engine.models.configuration import PortfolioDecisionConfigurationSnapshot

@pytest.fixture
def mock_execution_context():
    ctx = MagicMock(spec=PortfolioDecisionExecutionContext)
    ctx.portfolio_state_snapshot = MagicMock()
    ctx.portfolio_state_snapshot.snapshot_id = "state_1"
    ctx.portfolio_state_snapshot.dataset_version = "v1"
    ctx.portfolio_state_snapshot.parent_snapshot_references.portfolio_fingerprint = "fp_1"
    ctx.portfolio_state_snapshot.portfolio_state.active_positions = ["AAPL"]
    ctx.portfolio_state_snapshot.portfolio_state.metrics.total_portfolio_value = 100000.0

    ctx.portfolio_exposure_snapshot = MagicMock()
    ctx.portfolio_exposure_snapshot.snapshot_id = "exp_1"
    ctx.portfolio_exposure_snapshot.dataset_version = "v1"
    ctx.portfolio_exposure_snapshot.parent_snapshot_references.portfolio_fingerprint = "fp_1"
    ctx.portfolio_exposure_snapshot.exposure_analysis.gross_net_exposure.gross_exposure = 0.5
    ctx.portfolio_exposure_snapshot.exposure_analysis.gross_net_exposure.net_exposure = 0.2

    ctx.portfolio_correlation_snapshot = MagicMock()
    ctx.portfolio_correlation_snapshot.snapshot_id = "corr_1"
    ctx.portfolio_correlation_snapshot.business_fingerprint = "fp_1"
    ctx.portfolio_correlation_snapshot.parent_snapshot_references.dataset_version = "v1"
    ctx.portfolio_correlation_snapshot.correlation_analysis.symbol_correlation.pairwise_correlations = []
    ctx.portfolio_correlation_snapshot.correlation_metrics.average_correlation = 0.4

    ctx.risk_decision_snapshot = MagicMock()
    ctx.risk_decision_snapshot.snapshot_id = "risk_1"
    ctx.risk_decision_snapshot.business_fingerprint = "fp_1"
    ctx.risk_decision_snapshot.dataset_version = "v1"
    ctx.risk_decision_snapshot.report.final_decision_evidence.decision.value = "APPROVED"
    ctx.risk_decision_snapshot.metadata.additional_info = {"risk_amount": 500.0}

    ctx.candidate_position_snapshot = MagicMock()
    ctx.candidate_position_snapshot.snapshot_id = "cand_1"
    ctx.candidate_position_snapshot.business_fingerprint = "fp_1"
    ctx.candidate_position_snapshot.dataset_version = "v1"
    ctx.candidate_position_snapshot.symbol = "MSFT"
    ctx.candidate_position_snapshot.strategy_identifier = "MOMENTUM"
    ctx.candidate_position_snapshot.direction = "LONG"

    ctx.configuration = PortfolioDecisionConfigurationSnapshot(
        configuration_hash="hash_1",
        dataset_version="v1",
        pipeline_version="v1",
        rule_version="v1",
        limits={
            "max_gross_exposure": 1.0,
            "max_net_exposure": 0.5,
            "max_overall_correlation": 0.8,
            "max_symbol_correlation": 0.9,
            "max_active_positions": 20
        }
    )
    return ctx

@pytest.fixture
def pipeline_context(mock_execution_context):
    return PortfolioDecisionPipelineContext(
        execution_context=mock_execution_context,
        execution_id="exec_1"
    )

def test_structural_rules(mock_execution_context):
    rules = PortfolioDecisionStructuralRules()
    rules.validate(mock_execution_context)

    # Corrupt
    mock_execution_context.portfolio_state_snapshot = None
    with pytest.raises(ValueError):
        rules.validate(mock_execution_context)

def test_consistency_rules_fingerprint(mock_execution_context):
    rules = PortfolioDecisionConsistencyRules()
    rules.validate(mock_execution_context)

    # Mutate one parent's fingerprint to verify consistency rule failure
    mock_execution_context.portfolio_correlation_snapshot.business_fingerprint = "fp_2"
    with pytest.raises(ValueError, match="Business fingerprint mismatch"):
        rules.validate(mock_execution_context)

def test_consistency_rules_dataset(mock_execution_context):
    rules = PortfolioDecisionConsistencyRules()
    mock_execution_context.portfolio_state_snapshot.dataset_version = "v2"
    with pytest.raises(ValueError, match="Dataset version mismatch"):
        rules.validate(mock_execution_context)

def test_decision_aggregation_stage(pipeline_context):
    stage = DecisionAggregationStage()
    result = stage.execute(pipeline_context)

    facts = result.aggregated_facts
    assert facts["portfolio_state"]["active_positions_count"] == 1
    assert facts["portfolio_exposure"]["gross_exposure"] == 0.5
    assert facts["risk_decision"]["status"] == "APPROVED"

def test_decision_rules_stage_approved(pipeline_context):
    stage1 = DecisionAggregationStage()
    stage2 = DecisionRulesStage()
    
    ctx = stage1.execute(pipeline_context)
    ctx = stage2.execute(ctx)

    assert ctx.decision.status == DecisionStatus.APPROVED
    assert len(ctx.decision.reasons) == 1
    assert ctx.decision.reasons[0].code == "ALL_CHECKS_PASSED"

def test_decision_rules_stage_rejected(pipeline_context):
    # Set exposure over limit
    pipeline_context.execution_context.portfolio_exposure_snapshot.exposure_analysis.gross_net_exposure.gross_exposure = 1.5
    
    stage1 = DecisionAggregationStage()
    stage2 = DecisionRulesStage()
    
    ctx = stage1.execute(pipeline_context)
    ctx = stage2.execute(ctx)

    assert ctx.decision.status == DecisionStatus.REJECTED
    assert any(r.code == "PORTFOLIO_GROSS_EXPOSURE_LIMIT" for r in ctx.decision.reasons)

def test_decision_rules_collects_multiple_violations(pipeline_context):
    pipeline_context.execution_context.portfolio_exposure_snapshot.exposure_analysis.gross_net_exposure.gross_exposure = 1.5
    pipeline_context.execution_context.portfolio_exposure_snapshot.exposure_analysis.gross_net_exposure.net_exposure = 0.8
    pipeline_context.execution_context.risk_decision_snapshot.report.final_decision_evidence.decision.value = "REJECTED"
    
    stage1 = DecisionAggregationStage()
    stage2 = DecisionRulesStage()
    
    ctx = stage1.execute(pipeline_context)
    ctx = stage2.execute(ctx)

    assert ctx.decision.status == DecisionStatus.REJECTED
    reason_codes = [r.code for r in ctx.decision.reasons]
    assert "PORTFOLIO_GROSS_EXPOSURE_LIMIT" in reason_codes
    assert "PORTFOLIO_NET_EXPOSURE_LIMIT" in reason_codes
    assert "UPSTREAM_RISK_REJECTION" in reason_codes
