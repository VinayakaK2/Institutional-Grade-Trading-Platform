import abc
from typing import Dict, Any
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import StageResult

class ICertificationStage(abc.ABC):
    """
    Abstract base class for all certification verification stages.
    """
    
    @property
    @abc.abstractmethod
    def stage_name(self) -> str:
        """Explicit name of the certification stage."""
        pass
        
    @abc.abstractmethod
    async def execute(self, config: CertificationConfig, context: Dict[str, Any]) -> StageResult:
        """
        Executes the stage logic and returns the immutable result.
        
        Args:
            config: Full certification configuration.
            context: Shared dictionary for passing necessary artifacts (like instantiated engines or snapshots) down the pipeline.
        
        Returns:
            StageResult containing PASS/FAIL/SKIP and telemetry.
        """
        pass
