from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult
from backend.portfolio_optimization_engine.core.engine import PortfolioOptimizationEngine
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext
from backend.portfolio_optimization_engine.models.configuration import PortfolioOptimizationConfiguration
from unittest.mock import MagicMock
import time

def _recreate_execution_context_from_snapshot(snap) -> PortfolioOptimizationExecutionContext:
    """
    Recreates an execution context purely from the references to verify regression parity.
    """
    ctx = MagicMock(spec=PortfolioOptimizationExecutionContext)
    ctx.dataset_version = snap.dataset_version
    
    parents = snap.parent_snapshot_references
    
    ctx.portfolio_state_snapshot = MagicMock()
    ctx.portfolio_state_snapshot.snapshot_id = parents.portfolio_state_snapshot.snapshot_id
    ctx.portfolio_state_snapshot.dataset_version = parents.portfolio_state_snapshot.dataset_version
    ctx.portfolio_state_snapshot.schema_version = parents.portfolio_state_snapshot.snapshot_version
    ctx.portfolio_state_snapshot.business_fingerprint = parents.portfolio_state_snapshot.business_fingerprint

    ctx.portfolio_exposure_snapshot = MagicMock()
    ctx.portfolio_exposure_snapshot.snapshot_id = parents.portfolio_exposure_snapshot.snapshot_id
    ctx.portfolio_exposure_snapshot.dataset_version = parents.portfolio_exposure_snapshot.dataset_version
    ctx.portfolio_exposure_snapshot.schema_version = parents.portfolio_exposure_snapshot.snapshot_version
    ctx.portfolio_exposure_snapshot.business_fingerprint = parents.portfolio_exposure_snapshot.business_fingerprint

    ctx.portfolio_correlation_snapshot = MagicMock()
    ctx.portfolio_correlation_snapshot.snapshot_id = parents.portfolio_correlation_snapshot.snapshot_id
    ctx.portfolio_correlation_snapshot.dataset_version = parents.portfolio_correlation_snapshot.dataset_version
    ctx.portfolio_correlation_snapshot.schema_version = parents.portfolio_correlation_snapshot.snapshot_version
    ctx.portfolio_correlation_snapshot.business_fingerprint = parents.portfolio_correlation_snapshot.business_fingerprint

    ctx.portfolio_decision_snapshot = MagicMock()
    ctx.portfolio_decision_snapshot.snapshot_id = parents.portfolio_decision_snapshot.snapshot_id
    ctx.portfolio_decision_snapshot.dataset_version = parents.portfolio_decision_snapshot.dataset_version
    ctx.portfolio_decision_snapshot.schema_version = parents.portfolio_decision_snapshot.snapshot_version
    ctx.portfolio_decision_snapshot.business_fingerprint = parents.portfolio_decision_snapshot.business_fingerprint
    
    # We must mock the decision as "APPROVED" since optimization requires it, 
    # but the snapshot reference doesn't hold the decision status.
    # We assume valid input.
    ctx.portfolio_decision_snapshot.decision = "APPROVED"
    ctx.portfolio_decision_snapshot.lineage = MagicMock()
    ctx.portfolio_decision_snapshot.lineage.portfolio_state_snapshot.snapshot_id = parents.portfolio_state_snapshot.snapshot_id
    ctx.portfolio_decision_snapshot.lineage.portfolio_exposure_snapshot.snapshot_id = parents.portfolio_exposure_snapshot.snapshot_id
    ctx.portfolio_decision_snapshot.lineage.portfolio_correlation_snapshot.snapshot_id = parents.portfolio_correlation_snapshot.snapshot_id
    
    # The snapshot config hash is tested, but we need targets. 
    # Since regression just ensures fingerprint parity and we don't store targets in the canonical snapshot, 
    # we use synthetic targets. As long as they are consistent, determinism will match if the engine hasn't changed.
    # Actually, the configuration hash comes from the snapshot.
    ctx.configuration = PortfolioOptimizationConfiguration(
        configuration_hash=snap.configuration_snapshot_id,
        dataset_version=snap.dataset_version,
        pipeline_version="v1",
        optimization_targets={}
    )
    return ctx

async def verify_regression(context: PortfolioCertificationExecutionContext) -> CertificationStageResult:
    start_time = time.perf_counter()
    try:
        ref_snap = context.portfolio_optimization_snapshot
        
        repo = MemoryPortfolioOptimizationRepository()
        engine = PortfolioOptimizationEngine(repository=repo)
        opt_ctx = _recreate_execution_context_from_snapshot(ref_snap)
        
        # 2. Run Engine (Re-generate PortfolioOptimizationSnapshot)
        new_snap = await engine.optimize(opt_ctx)
        
        # Verify: Current Portfolio Engine == Certified Reference Output
        # Compare Configuration Hash
        if getattr(new_snap, 'configuration_snapshot_id', getattr(new_snap, 'configuration_hash', '')) != ref_snap.configuration_snapshot_id:
            raise ValueError("Regression failure: Configuration Hash changed.")
            
        # Compare Business Fingerprint
        if new_snap.business_fingerprint != ref_snap.business_fingerprint:
            raise ValueError(f"Regression failure: Business Fingerprint changed. Expected {ref_snap.business_fingerprint}, got {new_snap.business_fingerprint}")
            
        end_time = time.perf_counter()
        return CertificationStageResult(
            stage_name="Regression Verification",
            status="PASS",
            metrics={"execution_time_ms": (end_time - start_time) * 1000},
            error_message=None
        )
    except Exception as e:
        return CertificationStageResult(
            stage_name="Regression Verification",
            status="FAIL",
            metrics={},
            error_message=str(e)
        )
