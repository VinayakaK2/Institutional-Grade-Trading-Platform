from abc import ABC, abstractmethod
from backend.consolidation_engine.quality.models import ConsolidationEvaluationContext

class IQualityMetric(ABC):
    """
    Contract for an independent quality metric.
    Metrics must be pure, deterministic, and isolated.
    """
    
    @abstractmethod
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """
        Evaluates the metric and returns a score, typically between 0.0 and 1.0.
        (For duration, it may return the absolute candle count or a scaled score).
        """
        pass

class RangeStabilityMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Score based on how stable the prices are within the boundaries."""
        if not context.candles:
            return 0.0
        # Stub logic: return 1.0 for perfect stability
        return 1.0

class BoundaryRespectMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Score based on how cleanly candles respect the upper/lower boundaries without wicking too far out."""
        if not context.candles:
            return 0.0
        return 1.0

class PriceContainmentMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Score based on how tightly price is contained between boundaries."""
        if not context.candles:
            return 0.0
        return 1.0

class CandleConsistencyMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Score based on the visual consistency/sizing of the candles."""
        if not context.candles:
            return 0.0
        return 1.0

class ConsolidationDurationMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Returns the actual duration in candles."""
        return float(len(context.candles))

class RangeSymmetryMetric(IQualityMetric):
    def evaluate(self, context: ConsolidationEvaluationContext) -> float:
        """Score based on symmetry around the midpoint."""
        if not context.candles:
            return 0.0
        return 1.0
