from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from backend.consolidation_engine.lifecycle.models import (
    ConsolidationLifecycleContext,
    BaseLifecycleEvidence,
    ContinuationEvidence,
    WeakeningEvidence,
    BreakEvidence,
    EndEvidence
)

T = TypeVar('T', bound=BaseLifecycleEvidence)

class ILifecycleEvidenceEvaluator(ABC, Generic[T]):
    """
    Contract for an independent lifecycle evidence evaluator.
    Evaluators determine if sufficient evidence exists for their specific condition.
    """
    
    @abstractmethod
    def evaluate(self, context: ConsolidationLifecycleContext) -> T:
        """Returns the specific evidence object (e.g., BreakEvidence)."""
        pass

class ContinuationEvidenceEvaluator(ILifecycleEvidenceEvaluator[ContinuationEvidence]):
    def evaluate(self, context: ConsolidationLifecycleContext) -> ContinuationEvidence:
        """Checks if there's evidence that consolidation is continuing."""
        # Stub logic for Phase 8.4 boundary
        return ContinuationEvidence(
            triggered=False,
            confidence=0.0,
            reason="Continuation evaluation stub"
        )

class WeakeningEvidenceEvaluator(ILifecycleEvidenceEvaluator[WeakeningEvidence]):
    def evaluate(self, context: ConsolidationLifecycleContext) -> WeakeningEvidence:
        """Checks if there's evidence that consolidation is weakening."""
        # Stub logic
        return WeakeningEvidence(
            triggered=False,
            confidence=0.0,
            reason="Weakening evaluation stub"
        )

class BreakEvidenceEvaluator(ILifecycleEvidenceEvaluator[BreakEvidence]):
    def evaluate(self, context: ConsolidationLifecycleContext) -> BreakEvidence:
        """Checks if price action has broken out of the consolidation."""
        # Stub logic
        return BreakEvidence(
            triggered=False,
            confidence=0.0,
            reason="Break evaluation stub"
        )

class EndEvidenceEvaluator(ILifecycleEvidenceEvaluator[EndEvidence]):
    def evaluate(self, context: ConsolidationLifecycleContext) -> EndEvidence:
        """Checks if consolidation has completely ended (e.g., trend established)."""
        # Stub logic
        return EndEvidence(
            triggered=False,
            confidence=0.0,
            reason="End evaluation stub"
        )
