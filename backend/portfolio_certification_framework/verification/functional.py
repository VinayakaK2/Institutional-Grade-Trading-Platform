from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult
import time

async def verify_functional(context: PortfolioCertificationExecutionContext) -> CertificationStageResult:
    start_time = time.perf_counter()
    
    try:
        snap = context.portfolio_optimization_snapshot
        
        # Verify valid snapshot
        if not snap.optimization_result:
            raise ValueError("Missing optimization result.")
            
        # Verify lineage
        if not snap.parent_snapshot_references:
            raise ValueError("Missing parent snapshot references.")
            
        # Verify dataset version
        if snap.dataset_version != context.dataset_version:
            raise ValueError(f"Dataset mismatch: {snap.dataset_version} != {context.dataset_version}")
            
        # Verify configuration hash
        if snap.configuration_snapshot_id != context.configuration_snapshot_id:
            raise ValueError("Configuration mismatch.")
            
        end_time = time.perf_counter()
        return CertificationStageResult(
            stage_name="Functional Verification",
            status="PASS",
            metrics={"execution_time_ms": (end_time - start_time) * 1000},
            error_message=None
        )
    except Exception as e:
        return CertificationStageResult(
            stage_name="Functional Verification",
            status="FAIL",
            metrics={},
            error_message=str(e)
        )
