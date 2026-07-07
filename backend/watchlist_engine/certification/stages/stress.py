"""
Stress & Scalability Verification Stage
=======================================

Verifies behavior using progressively larger datasets and consecutive updates.
"""
import time
import traceback
from typing import List

from backend.watchlist_engine.certification.contracts import ICertificationStage
from backend.watchlist_engine.certification.models import CertificationStageResult, CertificationContext


class StressVerificationStage(ICertificationStage):
    """
    Executes stress and scalability checks (100, 500, 1000 symbols).
    """
    
    @property
    def name(self) -> str:
        return "StressVerificationStage"
        
    async def execute(self, context: CertificationContext) -> CertificationStageResult:
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        
        try:
            generator = context.dataset_generator
            engine = context.build_engine()
            
            # 1. Scale testing (100, 500, 1000)
            sizes = [100, 500, 1000]
            for size in sizes:
                candidates = generator.generate_candidates("standard", size)
                result = await engine.generate_watchlist(
                    run_id=f"stress_scale_{size}",
                    candidates=candidates,
                    source_universe_snapshot_id="mock_universe",
                    source_universe_version=1,
                    candidate_selection_version="v1.0.0",
                    config_hash="test_config"
                )
                if not result.snapshot:
                    errors.append(f"Stress test failed for size {size}: No snapshot generated.")
                elif len(result.snapshot.candidates) != size:
                    errors.append(f"Stress test size mismatch: expected {size}, got {len(result.snapshot.candidates)}")
                    
            # 2. Repeated Incremental Updates
            # Ensure memory doesn't blow up (simple sys.getsizeof check or just ensuring it doesn't crash)
            incremental_candidates = generator.generate_candidates("standard", 100)
            for i in range(10): # 10 consecutive executions
                await engine.generate_watchlist(
                    run_id=f"stress_inc_{i}",
                    candidates=incremental_candidates,
                    source_universe_snapshot_id="mock_universe",
                    source_universe_version=1,
                    candidate_selection_version="v1.0.0",
                    config_hash="test_config"
                )
                
        except Exception as e:
            errors.append(f"Unexpected error during stress verification: {str(e)}")
            errors.append(traceback.format_exc())
            
        execution_time = (time.time() - start_time) * 1000
        
        return CertificationStageResult(
            stage_name=self.name,
            passed=len(errors) == 0,
            execution_time_ms=execution_time,
            errors=errors,
            warnings=warnings
        )
