from abc import ABC, abstractmethod
import time

from backend.liquidity_grab_engine.certification.models.models import CertificationPhaseResult, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.generator.generator import DeterministicDatasetGenerator
from backend.liquidity_grab_engine.optimization.engine.engine import LiquidityGrabOptimizationEngine
from backend.liquidity_grab_engine.optimization.models.models import OptimizationContext

class BaseVerificationStrategy(ABC):
    def __init__(self, engine: LiquidityGrabOptimizationEngine):
        self._engine = engine
        
    @abstractmethod
    async def verify(self) -> CertificationPhaseResult:
        pass

class FunctionalVerificationStrategy(BaseVerificationStrategy):
    """
    Verifies that the full pipeline (via optimization wrapper) executes 
    without errors on standard deterministic datasets.
    """
    async def verify(self) -> CertificationPhaseResult:
        start_time = time.time()
        success = True
        error_msg = None
        
        try:
            datasets = [
                DeterministicDatasetGenerator.generate_valid_liquidity_grab(),
                DeterministicDatasetGenerator.generate_failed_recovery(),
                DeterministicDatasetGenerator.generate_false_break(),
                DeterministicDatasetGenerator.generate_empty_dataset()
            ]
            
            # Use cache disabled to ensure full functional run
            ctx = OptimizationContext(cache_enabled=False, reuse_enabled=False)
            results = await self._engine.execute_batch(datasets, ctx)
            
            if len(results) != len(datasets):
                success = False
                error_msg = f"Expected {len(datasets)} results, got {len(results)}"
                
        except Exception as e:
            success = False
            error_msg = str(e)
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return CertificationPhaseResult(
            phase=CertificationPhaseEnum.FOUNDATION, # Functional covers all core phases implicitly
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_msg,
            metrics={"datasets_tested": 4}
        )
