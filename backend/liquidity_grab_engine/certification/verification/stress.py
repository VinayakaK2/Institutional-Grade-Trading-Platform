import time
from backend.liquidity_grab_engine.certification.models.models import CertificationPhaseResult, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.generator.generator import DeterministicDatasetGenerator
from backend.liquidity_grab_engine.optimization.models.models import OptimizationContext
from backend.liquidity_grab_engine.certification.verification.functional import BaseVerificationStrategy

class StressVerificationStrategy(BaseVerificationStrategy):
    """
    Verifies that the system can handle large batches of candidates without failure.
    """
    def __init__(self, engine, stress_test_sizes):
        super().__init__(engine)
        self.stress_test_sizes = stress_test_sizes

    async def verify(self) -> CertificationPhaseResult:
        start_time = time.time()
        success = True
        error_msg = None
        metrics = {}
        
        try:
            for size in self.stress_test_sizes:
                datasets = DeterministicDatasetGenerator.generate_stress_dataset(size, version=3)
                ctx = OptimizationContext(cache_enabled=False, reuse_enabled=False, batch_size=100, max_parallelism=10)
                
                size_start = time.time()
                results = await self._engine.execute_batch(datasets, ctx)
                size_duration = (time.time() - size_start) * 1000.0
                
                metrics[f"duration_for_{size}"] = size_duration
                
                if len(results) != size:
                    success = False
                    error_msg = f"Stress test failed for size {size}: expected {size} results, got {len(results)}"
                    break

        except Exception as e:
            success = False
            error_msg = str(e)
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return CertificationPhaseResult(
            phase=CertificationPhaseEnum.LIFECYCLE, # Mapping stress testing to lifecycle scalability
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_msg,
            metrics=metrics
        )
