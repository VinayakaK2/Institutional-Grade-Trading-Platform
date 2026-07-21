import abc
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import RiskEvidenceBase

class IRiskMetricStage(abc.ABC):
    """
    Contract for a risk metric pipeline stage.
    """
    @property
    @abc.abstractmethod
    def stage_name(self) -> str:
        pass
        
    @abc.abstractmethod
    async def calculate(self, context: PositionRiskEvaluationContext) -> RiskEvidenceBase:
        """
        Executes the metric calculation and returns structured evidence.
        """
        pass
