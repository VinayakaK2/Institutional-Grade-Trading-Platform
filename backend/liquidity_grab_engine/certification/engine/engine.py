import time
import hashlib
import logging
import platform
from typing import List

from backend.liquidity_grab_engine.certification.models.models import (
    CertificationContext,
    CertificationReport,
    CertificationSummary,
    CertificationPhaseResult
)
from backend.liquidity_grab_engine.certification.contracts.repository import ICertificationRepository
from backend.liquidity_grab_engine.optimization.engine.engine import LiquidityGrabOptimizationEngine
from backend.liquidity_grab_engine.certification.verification.functional import FunctionalVerificationStrategy
from backend.liquidity_grab_engine.certification.verification.determinism import DeterminismVerificationStrategy
from backend.liquidity_grab_engine.certification.verification.stress import StressVerificationStrategy
from backend.liquidity_grab_engine.certification.verification.performance import PerformanceVerificationStrategy
from backend.liquidity_grab_engine.certification.verification.repository import RepositoryVerificationStrategy

logger = logging.getLogger(__name__)

class LiquidityGrabCertificationEngine:
    """
    Executes all certification strategies and produces the final immutable Certification Report.
    """
    def __init__(
        self,
        optimization_engine: LiquidityGrabOptimizationEngine,
        repository: ICertificationRepository,
        engine_version: str = "1.0.0"
    ):
        self._optimization_engine = optimization_engine
        self._repository = repository
        self._engine_version = engine_version
        
        # Instantiate strategies
        self._strategies = [
            FunctionalVerificationStrategy(self._optimization_engine),
            DeterminismVerificationStrategy(self._optimization_engine),
            RepositoryVerificationStrategy(self._optimization_engine),
            StressVerificationStrategy(self._optimization_engine, [100, 500, 1000]),
            PerformanceVerificationStrategy(self._optimization_engine)
        ]

    def _generate_report_id(self, timestamp: float) -> str:
        payload = f"CERT_{timestamp}_{self._engine_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    async def execute(self, context: CertificationContext) -> CertificationReport:
        start_time = time.time()
        logger.info("Starting Liquidity Grab Certification")
        
        # We might override strategies based on context.
        active_strategies = list(self._strategies)
        if not context.run_performance_benchmarks:
            active_strategies = [s for s in active_strategies if not isinstance(s, PerformanceVerificationStrategy)]
        
        phase_results: List[CertificationPhaseResult] = []
        is_certified = True
        
        for strategy in active_strategies:
            logger.info(f"Executing {strategy.__class__.__name__}")
            result = await strategy.verify()
            phase_results.append(result)
            
            if not result.success:
                logger.error(f"{strategy.__class__.__name__} failed: {result.error_message}")
                is_certified = False
                if context.fail_fast:
                    logger.warning("Fail fast enabled, halting certification.")
                    break
        
        total_time_ms = (time.time() - start_time) * 1000.0
        
        summary = CertificationSummary(
            is_certified=is_certified,
            total_execution_time_ms=total_time_ms,
            phase_results=phase_results
        )
        
        
        environment_details = {
            "engine_version": self._engine_version,
            "python_version": platform.python_version(),
            "operating_system": platform.system(),
            "os_release": platform.release(),
            "cpu_model": platform.processor(),
            "dataset_size": sum(context.stress_test_sizes), # Approximate
            "candidate_count": sum(context.stress_test_sizes)
        }
        
        # Merge explicitly provided env metadata
        environment_details.update(context.environment_metadata)
        
        report = CertificationReport(
            report_id=self._generate_report_id(start_time),
            dataset_metadata={"type": "Deterministic Synthetic", "seed": context.random_seed},
            environment_details=environment_details,
            summary=summary
        )
        
        await self._repository.save(report)
        logger.info(f"Certification completed. Result: {'PASS' if is_certified else 'FAIL'}")
        
        return report
