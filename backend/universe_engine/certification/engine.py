from datetime import datetime, timezone
from typing import Optional
import uuid
import subprocess # nosec
from backend.core.logger import get_logger
from backend.universe_engine.contracts.certification import IUniverseCertificationRepository, IUniverseCertificationFacade
from backend.universe_engine.certification.models import (
    UniverseCertificationConfiguration,
    UniverseCertificationContext,
    CertificationReport,
    UniverseCertificationResult
)
from backend.universe_engine.certification.pipeline import UniverseCertificationPipeline

logger = get_logger(__name__)

class UniverseCertificationEngine:
    """
    Automates the end-to-end certification of the Universe Engine.
    Uses Dependency Injection to receive the pre-configured engine facade,
    executes the certification pipeline, and persists an immutable report.
    """
    
    def __init__(
        self,
        config: UniverseCertificationConfiguration,
        pipeline: UniverseCertificationPipeline,
        repository: IUniverseCertificationRepository,
        facade: IUniverseCertificationFacade,
        pipeline_version: str = "1.0.0",
        business_fingerprint_version: str = "1.0.0"
    ):
        self._config = config
        self._pipeline = pipeline
        self._repository = repository
        self._facade = facade
        self._pipeline_version = pipeline_version
        self._business_fingerprint_version = business_fingerprint_version
        
    def _get_git_commit_hash(self) -> "Optional[str]":
        """Attempts to retrieve the current git commit hash, safely falling back to None."""
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT).decode('utf-8').strip() # nosec
        except Exception:
            return None

    async def generate_certification(self, run_id: str = None) -> UniverseCertificationResult:
        """
        Executes the full certification suite.
        """
        run_id = run_id or str(uuid.uuid4())
        logger.info(f"Starting Universe Certification [Run: {run_id}] - Mode: {self._config.mode}")
        
        context = UniverseCertificationContext(
            run_id=run_id,
            config=self._config,
            started_at=datetime.now(timezone.utc)
        )
        
        # 1. Execute Pipeline
        context = await self._pipeline.execute(context, self._facade)
        
        # 2. Build Report
        # Note: config_hash can be a simple hash of the dict for now, or just str representation
        config_hash = str(hash(str(self._config.model_dump())))
        
        report = CertificationReport(
            certification_id=run_id,
            pipeline_version=self._pipeline_version,
            config_hash=config_hash,
            business_fingerprint_version=self._business_fingerprint_version,
            git_commit_hash=self._get_git_commit_hash(),
            created_at=datetime.now(timezone.utc),
            configuration_snapshot=self._config,
            functional_passed=context.functional_passed,
            determinism_passed=context.determinism_passed,
            integrity_passed=context.integrity_passed,
            stress_passed=context.stress_passed,
            is_certified=context.is_certified,
            test_results=context.test_results,
            determinism_results=context.determinism_results,
            performance_metrics=context.performance_metrics
        )
        
        # 3. Persist Report
        try:
            await self._repository.save_certification_report(report)
            logger.info(f"Successfully generated and saved Certification Report: {run_id}")
        except Exception as e:
            logger.error(f"Failed to persist Certification Report {run_id}: {str(e)}")
            raise
            
        return UniverseCertificationResult(report=report)
