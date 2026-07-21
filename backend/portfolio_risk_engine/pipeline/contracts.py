import abc
from typing import Dict
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase

class IPortfolioRiskStage(abc.ABC):
    """
    Contract for individual metric stages within the Portfolio Risk Pipeline.
    """
    
    @property
    @abc.abstractmethod
    def stage_name(self) -> str:
        """Name of the stage."""
        pass

    @abc.abstractmethod
    async def calculate(
        self, 
        context: PortfolioRiskContext,
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> PortfolioEvidenceBase:
        """
        Executes the metric stage logic using read-only inputs.
        Must return strongly typed evidence inherited from PortfolioEvidenceBase.
        """
        pass
