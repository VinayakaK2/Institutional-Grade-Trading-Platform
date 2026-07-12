import time
from backend.liquidity_grab_engine.certification.models.models import CertificationPhaseResult, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.generator.generator import DeterministicDatasetGenerator
from backend.liquidity_grab_engine.optimization.models.models import OptimizationContext
from backend.liquidity_grab_engine.certification.verification.functional import BaseVerificationStrategy

class PerformanceVerificationStrategy(BaseVerificationStrategy):
    """
    Benchmarks execution time and throughput for sequential vs optimized execution.
    Does not enforce hard thresholds.
    """
    async def verify(self) -> CertificationPhaseResult:
        start_time = time.time()
        success = True
        error_msg = None
        metrics = {}
        
        try:
            # 1. Generate Dataset
            test_size = 500
            datasets = DeterministicDatasetGenerator.generate_stress_dataset(test_size, version=4)
            
            # 2. Sequential Unoptimized
            ctx_seq = OptimizationContext(cache_enabled=False, reuse_enabled=False, batch_size=1, max_parallelism=1)
            seq_start = time.time()
            await self._engine.execute_batch(datasets, ctx_seq)
            seq_duration = time.time() - seq_start
            
            # 3. Optimized Parallel (Cache Disabled)
            ctx_opt = OptimizationContext(cache_enabled=False, reuse_enabled=False, batch_size=50, max_parallelism=10)
            opt_start = time.time()
            await self._engine.execute_batch(datasets, ctx_opt)
            opt_duration = time.time() - opt_start
            
            # 4. Cached Execution (Reuse Enabled)
            ctx_cache_populate = OptimizationContext(cache_enabled=True, reuse_enabled=True)
            await self._engine.execute_batch(datasets, ctx_cache_populate) # Populate
            
            cache_start = time.time()
            await self._engine.execute_batch(datasets, ctx_cache_populate) # Hit
            cache_duration = time.time() - cache_start
            
            # Record Metrics
            metrics["sequential_execution_time_sec"] = seq_duration
            metrics["optimized_execution_time_sec"] = opt_duration
            metrics["cached_execution_time_sec"] = cache_duration
            metrics["speedup_ratio_parallel"] = seq_duration / opt_duration if opt_duration > 0 else float('inf')
            metrics["speedup_ratio_cached"] = seq_duration / cache_duration if cache_duration > 0 else float('inf')
            metrics["candidates_processed"] = test_size
            metrics["throughput_candidates_per_sec"] = test_size / opt_duration if opt_duration > 0 else float('inf')

        except Exception as e:
            success = False
            error_msg = str(e)
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return CertificationPhaseResult(
            phase=CertificationPhaseEnum.OPTIMIZATION,
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_msg,
            metrics=metrics
        )
