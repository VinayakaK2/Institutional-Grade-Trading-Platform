import pytest
from unittest.mock import MagicMock
from backend.portfolio_decision_engine.core.engine import PortfolioDecisionEngine
from backend.portfolio_decision_engine.repository.memory_repo import MemoryPortfolioDecisionRepository
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionExecutionContext
from backend.portfolio_decision_engine.models.configuration import PortfolioDecisionConfigurationSnapshot
from backend.portfolio_decision_engine.models.decision_models import DecisionStatus

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
        pipeline_version="1.0.0",
        rule_version="1.0",
        limits={
            "max_gross_exposure": 1.0,
            "max_net_exposure": 0.5,
            "max_overall_correlation": 0.8,
            "max_symbol_correlation": 0.9,
            "max_active_positions": 20
        }
    )
    return ctx

def test_engine_execution_success(mock_execution_context):
    repo = MemoryPortfolioDecisionRepository()
    engine = PortfolioDecisionEngine(repo)

    snapshot = engine.evaluate(mock_execution_context)

    assert snapshot is not None
    assert snapshot.decision.status == DecisionStatus.APPROVED
    assert snapshot.configuration_snapshot_id == "hash_1"
    assert snapshot.business_fingerprint == "fp_1"
    assert repo.exists(snapshot.snapshot_id)

def test_engine_structural_failure(mock_execution_context):
    mock_execution_context.portfolio_state_snapshot = None
    repo = MemoryPortfolioDecisionRepository()
    engine = PortfolioDecisionEngine(repo)

    with pytest.raises(ValueError):
        engine.evaluate(mock_execution_context)

def test_engine_snapshot_determinism(mock_execution_context):
    """
    Run identical inputs 100 times to verify exact same hash is generated.
    """
    engine = PortfolioDecisionEngine(MemoryPortfolioDecisionRepository())
    
    first_snapshot = engine.evaluate(mock_execution_context)
    first_hash = first_snapshot.snapshot_id

    for _ in range(100):
        # We must use a new repo or we'll get "already exists" errors 
        # because the ID is deterministic.
        repo = MemoryPortfolioDecisionRepository()
        engine = PortfolioDecisionEngine(repo)
        snap = engine.evaluate(mock_execution_context)
        assert snap.snapshot_id == first_hash

def test_engine_config_hash_validation(mock_execution_context):
    repo = MemoryPortfolioDecisionRepository()
    engine = PortfolioDecisionEngine(repo)
    
    first_snapshot = engine.evaluate(mock_execution_context)
    
    # Modify configuration
    mock_execution_context.configuration = PortfolioDecisionConfigurationSnapshot(
        configuration_hash="hash_2", # changed
        dataset_version="v1",
        pipeline_version="v1",
        rule_version="v2",
        limits={
            "max_gross_exposure": 1.0,
        }
    )
    
    repo2 = MemoryPortfolioDecisionRepository()
    engine2 = PortfolioDecisionEngine(repo2)
    second_snapshot = engine2.evaluate(mock_execution_context)
    
    assert first_snapshot.snapshot_id != second_snapshot.snapshot_id
    assert second_snapshot.configuration_snapshot_id == "hash_2"
