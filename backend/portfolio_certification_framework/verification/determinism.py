from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult
from backend.portfolio_optimization_engine.core.engine import PortfolioOptimizationEngine
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext
from backend.portfolio_optimization_engine.models.configuration import PortfolioOptimizationConfiguration
from unittest.mock import MagicMock
import time

def build_synthetic_optimization_context(seed: str = "seed") -> PortfolioOptimizationExecutionContext:
    ctx = MagicMock(spec=PortfolioOptimizationExecutionContext)
    ctx.dataset_version = "v1"
    
    ctx.portfolio_state_snapshot = MagicMock()
    ctx.portfolio_state_snapshot.snapshot_id = f"state_{seed}"
    ctx.portfolio_state_snapshot.dataset_version = "v1"
    ctx.portfolio_state_snapshot.schema_version = "1.0"
    ctx.portfolio_state_snapshot.business_fingerprint = f"fp_state_{seed}"

    ctx.portfolio_exposure_snapshot = MagicMock()
    ctx.portfolio_exposure_snapshot.snapshot_id = f"exp_{seed}"
    ctx.portfolio_exposure_snapshot.dataset_version = "v1"
    ctx.portfolio_exposure_snapshot.schema_version = "1.0"
    ctx.portfolio_exposure_snapshot.business_fingerprint = f"fp_exp_{seed}"

    ctx.portfolio_correlation_snapshot = MagicMock()
    ctx.portfolio_correlation_snapshot.snapshot_id = f"corr_{seed}"
    ctx.portfolio_correlation_snapshot.dataset_version = "v1"
    ctx.portfolio_correlation_snapshot.schema_version = "1.0"
    ctx.portfolio_correlation_snapshot.business_fingerprint = f"fp_corr_{seed}"

    ctx.portfolio_decision_snapshot = MagicMock()
    ctx.portfolio_decision_snapshot.snapshot_id = f"dec_{seed}"
    ctx.portfolio_decision_snapshot.dataset_version = "v1"
    ctx.portfolio_decision_snapshot.schema_version = "1.0"
    ctx.portfolio_decision_snapshot.business_fingerprint = f"fp_dec_{seed}"
    ctx.portfolio_decision_snapshot.decision = "APPROVED"
    
    ctx.portfolio_decision_snapshot.lineage = MagicMock()
    ctx.portfolio_decision_snapshot.lineage.portfolio_state_snapshot.snapshot_id = f"state_{seed}"
    ctx.portfolio_decision_snapshot.lineage.portfolio_exposure_snapshot.snapshot_id = f"exp_{seed}"
    ctx.portfolio_decision_snapshot.lineage.portfolio_correlation_snapshot.snapshot_id = f"corr_{seed}"
    
    ctx.configuration = PortfolioOptimizationConfiguration(
        configuration_hash=f"hash_{seed}",
        dataset_version="v1",
        pipeline_version="v1",
        optimization_targets={"target_weight": 0.05}
    )
    return ctx

async def verify_determinism(context: PortfolioCertificationExecutionContext) -> CertificationStageResult:
    start_time = time.perf_counter()
    try:
        repo = MemoryPortfolioOptimizationRepository()
        engine = PortfolioOptimizationEngine(repository=repo)
        
        opt_ctx = build_synthetic_optimization_context("determinism")
        
        # 1. Sequential Execution
        snap1 = await engine.optimize(opt_ctx)
        
        # 2. Repeated Execution
        snap2 = await engine.optimize(opt_ctx)
        
        if snap1.business_fingerprint != snap2.business_fingerprint:
            raise ValueError(f"Fingerprint mismatch: {snap1.business_fingerprint} != {snap2.business_fingerprint}")
            
        end_time = time.perf_counter()
        return CertificationStageResult(
            stage_name="Determinism Verification",
            status="PASS",
            metrics={"execution_time_ms": (end_time - start_time) * 1000},
            error_message=None
        )
    except Exception as e:
        return CertificationStageResult(
            stage_name="Determinism Verification",
            status="FAIL",
            metrics={},
            error_message=str(e)
        )
