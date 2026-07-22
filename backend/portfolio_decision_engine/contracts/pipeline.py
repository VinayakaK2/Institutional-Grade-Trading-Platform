import abc
from backend.portfolio_decision_engine.models.contexts import PortfolioDecisionPipelineContext

class IDecisionStage(abc.ABC):
    """
    Strict boundary for decision pipeline stages.
    Enforces a single explicit execute function that transforms the mutable pipeline context.
    """
    @abc.abstractmethod
    def execute(self, context: PortfolioDecisionPipelineContext) -> PortfolioDecisionPipelineContext:
        pass
