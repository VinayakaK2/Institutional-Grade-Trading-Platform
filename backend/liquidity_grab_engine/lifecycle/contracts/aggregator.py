from abc import ABC, abstractmethod
from backend.liquidity_grab_engine.lifecycle.models.models import LifecycleEvidence, LifecycleSummary

class ILifecycleAggregator(ABC):
    @abstractmethod
    def aggregate(self, evidence: LifecycleEvidence) -> LifecycleSummary:
        """
        Applies deterministic precedence to the collected evidence to produce a lifecycle state.
        Precedence: FAILED > EXPIRED > WEAKENING > CONTINUING > ACTIVE
        """
        pass
