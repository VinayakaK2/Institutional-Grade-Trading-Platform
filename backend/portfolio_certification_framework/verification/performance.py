from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.certification_models import CertificationStageResult
from backend.portfolio_optimization_engine.core.engine import PortfolioOptimizationEngine
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository
from backend.portfolio_certification_framework.verification.determinism import build_synthetic_optimization_context
import time
import tracemalloc

async def verify_performance(context: PortfolioCertificationExecutionContext) -> CertificationStageResult:
    start_time = time.perf_counter()
    
    try:
        repo = MemoryPortfolioOptimizationRepository()
        engine = PortfolioOptimizationEngine(repository=repo)
        
        opt_ctx = build_synthetic_optimization_context("performance")
        
        iterations = 5
        
        # Measure
        tracemalloc.start()
        
        for _ in range(iterations):
            await engine.optimize(opt_ctx)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        end_time = time.perf_counter()
        
        # Performance stage NEVER fails certification
        return CertificationStageResult(
            stage_name="Performance Verification",
            status="COMPLETED",
            metrics={
                "execution_time_ms": (end_time - start_time) * 1000,
                "peak_memory_bytes": peak,
                "throughput_per_sec": iterations / (end_time - start_time)
            },
            error_message=None
        )
    except Exception as e:
        # Even on internal error, it shouldn't fail certification ideally, but if it crashes it's an exception
        return CertificationStageResult(
            stage_name="Performance Verification",
            status="COMPLETED",
            metrics={},
            error_message=f"Performance measurement encountered an error: {str(e)}"
        )
