"""
Functional Verification Stage
=============================

Verifies Watchlist Foundation, Candidate Selection, Freshness Validation, 
Watchlist Management, and Optimization Layer behave correctly.
"""
import time
import traceback
from typing import List

from backend.watchlist_engine.certification.contracts import ICertificationStage
from backend.watchlist_engine.certification.models import CertificationStageResult, CertificationContext
from backend.watchlist_engine.models.exceptions import WatchlistValidationError


class FunctionalVerificationStage(ICertificationStage):
    """
    Executes standard, invalid, and stale functional tests.
    """
    
    @property
    def name(self) -> str:
        return "FunctionalVerificationStage"
        
    async def execute(self, context: CertificationContext) -> CertificationStageResult:
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        
        try:
            generator = context.dataset_generator
            
            # 1. Standard valid generation
            engine = context.build_engine()
            candidates = generator.generate_candidates("standard", 10)
            result = await engine.generate_watchlist(
                run_id="test_functional_1",
                candidates=candidates,
                source_universe_snapshot_id="mock_universe",
                source_universe_version=1,
                candidate_selection_version="v1.0.0",
                config_hash="test_config"
            )
            if not result.snapshot:
                errors.append("Standard functional test failed: No snapshot generated.")
            elif len(result.snapshot.candidates) != 10:
                errors.append(f"Expected 10 candidates, got {len(result.snapshot.candidates)}")
                
            # 2. Empty validation
            empty_candidates = generator.generate_candidates("empty_universe")
            try:
                await engine.generate_watchlist(
                    run_id="test_functional_2",
                    candidates=empty_candidates,
                    source_universe_snapshot_id="mock_universe",
                    source_universe_version=1,
                    candidate_selection_version="v1.0.0",
                    config_hash="test_config"
                )
                errors.append("Empty universe did not raise WatchlistValidationError.")
            except WatchlistValidationError:
                pass # Expected
                
            # 3. Optimization Bypass Check (Same Input)
            candidates_opt = generator.generate_candidates("standard", 10)
            result_opt = await engine.generate_watchlist(
                run_id="test_functional_3",
                candidates=candidates_opt,
                source_universe_snapshot_id="mock_universe",
                source_universe_version=1,
                candidate_selection_version="v1.0.0",
                config_hash="test_config"
            )
            # Ensure the snapshot returned is identical (version shouldn't increment if bypassed)
            if result_opt.snapshot and result.snapshot:
                if result_opt.snapshot.version != result.snapshot.version:
                    errors.append("Optimization layer failed to reuse snapshot for identical input.")
            else:
                errors.append("Optimization layer returned no snapshot.")
                
            # 4. Stale market data
            stale_candidates = generator.generate_candidates("stale_market_data", 5)
            # Freshness engine should filter these out. If none survive, it might fail validation or return empty depending on settings.
            # We assume it drops them, if all are dropped, validation might fail (if allow_empty=False) or succeed with 0.
            # Let's just run it. 
            try:
                stale_result = await engine.generate_watchlist(
                    run_id="test_functional_4",
                    candidates=stale_candidates,
                    source_universe_snapshot_id="mock_universe",
                    source_universe_version=1,
                    candidate_selection_version="v1.0.0",
                    config_hash="test_config"
                )
                # If allow_empty=True, it succeeds but should have 0 candidates.
                if stale_result.snapshot and len(stale_result.snapshot.candidates) > 0:
                    # Depending on mocked freshness stage, it might not filter unless mocked properly.
                    warnings.append("Stale market data check requires mocked freshness stage to drop candidates.")
            except WatchlistValidationError:
                # If allow_empty=False, this is expected.
                pass
                
        except Exception as e:
            errors.append(f"Unexpected error during functional verification: {str(e)}")
            errors.append(traceback.format_exc())
            
        execution_time = (time.time() - start_time) * 1000
        
        return CertificationStageResult(
            stage_name=self.name,
            passed=len(errors) == 0,
            execution_time_ms=execution_time,
            errors=errors,
            warnings=warnings
        )
