from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.repository.local_evidence_repository import LocalEvidenceRepository
from backend.trade_validation_engine.certification.engine.certification_engine import TradeValidationCertificationEngine
from backend.trade_validation_engine.certification.stages.functional_verification_stage import FunctionalVerificationStage
from backend.trade_validation_engine.certification.stages.determinism_verification_stage import DeterminismVerificationStage
from backend.trade_validation_engine.certification.stages.repository_verification_stage import RepositoryVerificationStage
from backend.trade_validation_engine.certification.stages.regression_verification_stage import RegressionVerificationStage
from backend.trade_validation_engine.certification.stages.stress_verification_stage import StressVerificationStage
from backend.trade_validation_engine.certification.stages.performance_verification_stage import PerformanceVerificationStage

class CertificationContainer:
    """
    Dependency Injection Container for Certification Layer.
    """
    def __init__(self, config: CertificationConfig = None):
        self._config = config or CertificationConfig()
        
    def repository(self) -> LocalEvidenceRepository:
        return LocalEvidenceRepository(self._config)
        
    def engine(self) -> TradeValidationCertificationEngine:
        stages = [
            FunctionalVerificationStage(),
            DeterminismVerificationStage(),
            RepositoryVerificationStage(),
            RegressionVerificationStage(),
            StressVerificationStage(),
            PerformanceVerificationStage()
        ]
        return TradeValidationCertificationEngine(
            config=self._config,
            repository=self.repository(),
            stages=stages
        )
