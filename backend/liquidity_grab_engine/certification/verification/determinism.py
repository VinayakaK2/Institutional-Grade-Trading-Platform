import time
from backend.liquidity_grab_engine.certification.models.models import CertificationPhaseResult, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.generator.generator import DeterministicDatasetGenerator
from backend.liquidity_grab_engine.optimization.models.models import OptimizationContext
from backend.liquidity_grab_engine.certification.verification.functional import BaseVerificationStrategy

class DeterminismVerificationStrategy(BaseVerificationStrategy):
    """
    Verifies that Sequential output == Parallel output, and that
    Incremental output == Full pipeline output.
    """
    async def verify(self) -> CertificationPhaseResult:
        start_time = time.time()
        success = True
        error_msg = None
        
        try:
            # Generate 10 identical deterministic items
            datasets = DeterministicDatasetGenerator.generate_stress_dataset(10, version=2)
            
            # 1. Sequential Run (Cache Disabled, parallelism=1)
            ctx_seq = OptimizationContext(cache_enabled=False, reuse_enabled=False, batch_size=1, max_parallelism=1)
            seq_results = await self._engine.execute_batch(datasets, ctx_seq)
            
            # 2. Parallel Run (Cache Disabled, parallelism=5)
            ctx_par = OptimizationContext(cache_enabled=False, reuse_enabled=False, batch_size=5, max_parallelism=5)
            par_results = await self._engine.execute_batch(datasets, ctx_par)
            
            # 3. Incremental/Cached Run (Cache Enabled)
            ctx_cached = OptimizationContext(cache_enabled=True, reuse_enabled=True)
            # First run to populate
            await self._engine.execute_batch(datasets, ctx_cached)
            # Second run to hit cache
            cached_results = await self._engine.execute_batch(datasets, ctx_cached)
            
            # Verify Sequential == Parallel outputs (checking snapshot hashes)
            for i in range(len(datasets)):
                if seq_results[i].snapshot_id != par_results[i].snapshot_id:
                    success = False
                    error_msg = f"Determinism failure: Sequential != Parallel at index {i}"
                    break
                    
                if seq_results[i].snapshot_id != cached_results[i].snapshot_id:
                    success = False
                    error_msg = f"Determinism failure: Full Pipeline != Cached Output at index {i}"
                    break

        except Exception as e:
            success = False
            error_msg = str(e)
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return CertificationPhaseResult(
            phase=CertificationPhaseEnum.DETECTION, # Mapping determinism broadly to detection accuracy
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_msg,
            metrics={}
        )
