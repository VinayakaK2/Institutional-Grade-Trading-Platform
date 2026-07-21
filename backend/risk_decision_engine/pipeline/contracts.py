from abc import ABC, abstractmethod
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import DecisionEvidenceBase

class IRiskDecisionStage(ABC):
    @abstractmethod
    async def evaluate(self, context: RiskDecisionContext) -> DecisionEvidenceBase:
        pass
