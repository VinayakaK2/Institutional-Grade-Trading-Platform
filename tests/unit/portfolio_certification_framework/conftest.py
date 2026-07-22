import pytest
from unittest.mock import MagicMock
from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot
from backend.portfolio_optimization_engine.models.references import ParentSnapshotReferences, SnapshotReference

@pytest.fixture
def mock_certification_context():
    snap = MagicMock(spec=PortfolioOptimizationSnapshot)
    snap.snapshot_id = "opt_snap_1"
    snap.dataset_version = "v1"
    snap.configuration_snapshot_id = "hash_1"
    snap.business_fingerprint = "opt_fp_1"
    
    parent_refs = MagicMock(spec=ParentSnapshotReferences)
    
    state_ref = MagicMock(spec=SnapshotReference)
    state_ref.snapshot_id = "state_1"
    state_ref.snapshot_version = "1.0"
    state_ref.dataset_version = "v1"
    state_ref.business_fingerprint = "fp_state"
    parent_refs.portfolio_state_snapshot = state_ref
    
    exp_ref = MagicMock(spec=SnapshotReference)
    exp_ref.snapshot_id = "exp_1"
    exp_ref.snapshot_version = "1.0"
    exp_ref.dataset_version = "v1"
    exp_ref.business_fingerprint = "fp_exp"
    parent_refs.portfolio_exposure_snapshot = exp_ref
    
    corr_ref = MagicMock(spec=SnapshotReference)
    corr_ref.snapshot_id = "corr_1"
    corr_ref.snapshot_version = "1.0"
    corr_ref.dataset_version = "v1"
    corr_ref.business_fingerprint = "fp_corr"
    parent_refs.portfolio_correlation_snapshot = corr_ref
    
    dec_ref = MagicMock(spec=SnapshotReference)
    dec_ref.snapshot_id = "dec_1"
    dec_ref.snapshot_version = "1.0"
    dec_ref.dataset_version = "v1"
    dec_ref.business_fingerprint = "fp_dec"
    parent_refs.portfolio_decision_snapshot = dec_ref
    
    snap.parent_snapshot_references = parent_refs
    snap.optimization_result = MagicMock()
    
    ctx = PortfolioCertificationExecutionContext(
        portfolio_optimization_snapshot=snap,
        dataset_version="v1",
        configuration_snapshot_id="hash_1"
    )
    return ctx
