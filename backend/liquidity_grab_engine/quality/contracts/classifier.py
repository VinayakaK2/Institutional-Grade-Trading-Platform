from abc import ABC, abstractmethod
from backend.liquidity_grab_engine.quality.models.models import QualityEvidence, ClassificationSummary
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext

class IQualityClassifier(ABC):
    """
    Interface for determining overall quality classification based on collected evidence.
    """
    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def classify(self, evidence: QualityEvidence, context: LiquidityGrabEvaluationContext) -> ClassificationSummary:
        """Applies deterministic weighting to produce classification."""
        pass
