from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository
import time

async def verify_repository(context: PortfolioCertificationExecutionContext) -> CertificationStageResult:
    start_time = time.perf_counter()
    try:
        repo = MemoryPortfolioOptimizationRepository()
        snap = context.portfolio_optimization_snapshot
        
        if not snap:
            raise ValueError("Missing snapshot")
            
        assert snap is not None
        
        # 1. Insert-only / Immutable storage
        await repo.save(snap) # type: ignore
        
        # 2. Retrieval correctness
        loaded = await repo.load(snap.snapshot_id) # type: ignore
        if loaded.snapshot_id != snap.snapshot_id: # type: ignore
            raise ValueError("Retrieval correctness failed: ID mismatch.")
            
        # 3. Hash preservation
        if loaded.business_fingerprint != snap.business_fingerprint: # type: ignore
            raise ValueError("Hash preservation failed: Fingerprint mismatch.")
        
        end_time = time.perf_counter()
        return CertificationStageResult(
            stage_name="Repository Verification",
            status="PASS",
            metrics={"execution_time_ms": (end_time - start_time) * 1000},
            error_message=None
        )
    except Exception as e:
        return CertificationStageResult(
            stage_name="Repository Verification",
            status="FAIL",
            metrics={},
            error_message=str(e)
        )
