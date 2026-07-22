from abc import ABC, abstractmethod
from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext

class IPortfolioCertificationStage(ABC):
    """
    Interface for independent certification verification stages.
    """
    @abstractmethod
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        """
        Executes a verification stage sequentially and enriches the execution context with a CertificationStageResult.
        """
        pass
