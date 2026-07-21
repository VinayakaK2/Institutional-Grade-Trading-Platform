from abc import ABC, abstractmethod
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.report import ValidationResult

class IRiskDecisionValidationLayer(ABC):
    @abstractmethod
    async def validate(self, context: RiskDecisionContext) -> ValidationResult:
        pass
