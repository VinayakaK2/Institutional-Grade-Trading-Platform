"""
Determinism Verification Stage
==============================

Verifies sequential/parallel equivalence, incremental/full equivalence, 
and stable snapshot generation.
"""
import time
import traceback
from typing import List

from backend.watchlist_engine.certification.contracts import ICertificationStage
from backend.watchlist_engine.certification.models import (
    CertificationStageResult,
    CertificationContext
)
from backend.watchlist_engine.models.models import WatchlistCandidate
from backend.watchlist_engine.models.config import WatchlistOptimizationSettings


class DeterminismVerificationStage(ICertificationStage):
    """
    Executes explicit determinism checks.
    """
    
    @property
    def name(self) -> str:
        return "DeterminismVerificationStage"
        
    async def execute(self, context: CertificationContext) -> CertificationStageResult:
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        
        try:
            generator = context.dataset_generator
            
            # Helper to check equivalence
            def check_equivalence(name: str, snap1, snap2):
                if not snap1 or not snap2:
                    errors.append(f"{name} Equivalence failed: Missing snapshot.")
                    return
                if len(snap1.candidates) != len(snap2.candidates):
                    errors.append(f"{name} Equivalence failed: Length mismatch {len(snap1.candidates)} != {len(snap2.candidates)}")
                fp1 = snap1.metadata.get("business_fingerprint")
                fp2 = snap2.metadata.get("business_fingerprint")
                if fp1 != fp2:
                    errors.append(f"{name} Equivalence failed: Fingerprint mismatch {fp1} != {fp2}")

            candidates = generator.generate_candidates("standard", 50)
            
            # 1. Sequential vs Parallel
            seq_engine = context.build_engine(
                opt_settings=WatchlistOptimizationSettings(max_parallel_workers=1)
            )
            par_engine = context.build_engine(
                opt_settings=WatchlistOptimizationSettings(max_parallel_workers=4)
            )
            
            seq_result = await seq_engine.generate_watchlist(
                run_id="det_seq", candidates=candidates,
                source_universe_snapshot_id="mock_universe", source_universe_version=1,
                candidate_selection_version="v1.0.0", config_hash="test_config"
            )
            
            par_result = await par_engine.generate_watchlist(
                run_id="det_par", candidates=candidates,
                source_universe_snapshot_id="mock_universe", source_universe_version=1,
                candidate_selection_version="v1.0.0", config_hash="test_config"
            )
            
            check_equivalence("Sequential vs Parallel", seq_result.snapshot, par_result.snapshot)
            
            # 2. Incremental vs Full Rebuild
            # First run an initial set
            incremental_engine = context.build_engine()
            base_candidates = generator.generate_candidates("standard", 20)
            
            await incremental_engine.generate_watchlist(
                run_id="det_inc_base", candidates=base_candidates,
                source_universe_snapshot_id="mock_universe", source_universe_version=1,
                candidate_selection_version="v1.0.0", config_hash="test_config"
            )
            
            # Add one new candidate for incremental run
            new_sym = WatchlistCandidate(
                watchlist_symbol=generator._generate_watchlist_symbol(9999)
            )
            inc_candidates = base_candidates + [new_sym]
            
            inc_result = await incremental_engine.generate_watchlist(
                run_id="det_inc_update", candidates=inc_candidates,
                source_universe_snapshot_id="mock_universe", source_universe_version=1,
                candidate_selection_version="v1.0.0", config_hash="test_config"
            )
            
            # Full rebuild of the same updated candidates
            full_engine = context.build_engine() # new engine, empty history
            full_result = await full_engine.generate_watchlist(
                run_id="det_full", candidates=inc_candidates,
                source_universe_snapshot_id="mock_universe", source_universe_version=1,
                candidate_selection_version="v1.0.0", config_hash="test_config"
            )
            
            check_equivalence("Incremental vs Full Rebuild", inc_result.snapshot, full_result.snapshot)

        except Exception as e:
            errors.append(f"Unexpected error during determinism verification: {str(e)}")
            errors.append(traceback.format_exc())
            
        execution_time = (time.time() - start_time) * 1000
        
        return CertificationStageResult(
            stage_name=self.name,
            passed=len(errors) == 0,
            execution_time_ms=execution_time,
            errors=errors,
            warnings=warnings
        )
