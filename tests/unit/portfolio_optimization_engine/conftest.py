import pytest
from unittest.mock import MagicMock
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext, PortfolioOptimizationPipelineContext
from backend.portfolio_optimization_engine.models.configuration import PortfolioOptimizationConfiguration

@pytest.fixture
def mock_execution_context():
    ctx = MagicMock(spec=PortfolioOptimizationExecutionContext)
    ctx.dataset_version = "v1"
    
    ctx.portfolio_state_snapshot = MagicMock()
    ctx.portfolio_state_snapshot.snapshot_id = "state_1"
    ctx.portfolio_state_snapshot.dataset_version = "v1"
    ctx.portfolio_state_snapshot.schema_version = "1.0"
    ctx.portfolio_state_snapshot.business_fingerprint = "fp_state"

    ctx.portfolio_exposure_snapshot = MagicMock()
    ctx.portfolio_exposure_snapshot.snapshot_id = "exp_1"
    ctx.portfolio_exposure_snapshot.dataset_version = "v1"
    ctx.portfolio_exposure_snapshot.schema_version = "1.0"
    ctx.portfolio_exposure_snapshot.business_fingerprint = "fp_exp"

    ctx.portfolio_correlation_snapshot = MagicMock()
    ctx.portfolio_correlation_snapshot.snapshot_id = "corr_1"
    ctx.portfolio_correlation_snapshot.dataset_version = "v1"
    ctx.portfolio_correlation_snapshot.schema_version = "1.0"
    ctx.portfolio_correlation_snapshot.business_fingerprint = "fp_corr"

    ctx.portfolio_decision_snapshot = MagicMock()
    ctx.portfolio_decision_snapshot.snapshot_id = "dec_1"
    ctx.portfolio_decision_snapshot.dataset_version = "v1"
    ctx.portfolio_decision_snapshot.schema_version = "1.0"
    ctx.portfolio_decision_snapshot.business_fingerprint = "fp_dec"
    ctx.portfolio_decision_snapshot.decision = "APPROVED"
    
    # Lineage for decision
    ctx.portfolio_decision_snapshot.lineage = MagicMock()
    ctx.portfolio_decision_snapshot.lineage.portfolio_state_snapshot.snapshot_id = "state_1"
    ctx.portfolio_decision_snapshot.lineage.portfolio_exposure_snapshot.snapshot_id = "exp_1"
    ctx.portfolio_decision_snapshot.lineage.portfolio_correlation_snapshot.snapshot_id = "corr_1"
    
    ctx.configuration = PortfolioOptimizationConfiguration(
        configuration_hash="hash_1",
        dataset_version="v1",
        pipeline_version="v1",
        optimization_targets={"target_weight": 0.05}
    )
    return ctx

@pytest.fixture
def pipeline_context(mock_execution_context):
    return PortfolioOptimizationPipelineContext(
        execution_context=mock_execution_context,
        execution_id="exec_1"
    )
