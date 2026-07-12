from abc import ABC, abstractmethod
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext
from backend.liquidity_grab_engine.quality.models.models import MetricResult

class IMetric(ABC):
    """Base interface for all quality metrics."""
    @property
    @abstractmethod
    def metric_id(self) -> str:
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, context: LiquidityGrabEvaluationContext) -> MetricResult:
        pass

class ISupportRecoveryMetric(IMetric):
    pass

class IRecoveryStrengthMetric(IMetric):
    pass

class IRecoverySpeedMetric(IMetric):
    pass

class IFalseBreakDepthMetric(IMetric):
    pass

class IVolumeConfirmationMetric(IMetric):
    pass

class IStructuralConsistencyMetric(IMetric):
    pass
