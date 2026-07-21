from typing import List, Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase
from backend.portfolio_risk_engine.exceptions.exceptions import PortfolioRiskPipelineError

class PortfolioRiskPipeline:
    """
    Orchestrates the portfolio risk metric calculation stages.
    """
    def __init__(self, stages: List[IPortfolioRiskStage]):
        self._stages = stages
        
    async def execute(self, context: PortfolioRiskContext, provider: IPortfolioSnapshotProvider) -> Dict[str, PortfolioEvidenceBase]:
        evidence_bag: Dict[str, PortfolioEvidenceBase] = {}
        
        for stage in self._stages:
            try:
                evidence = await stage.calculate(context, provider, evidence_bag)
                evidence_bag[stage.stage_name] = evidence
            except Exception as e:
                if context.configuration.fail_fast:
                    raise PortfolioRiskPipelineError(f"Pipeline failed at stage {stage.stage_name}: {str(e)}") from e
                
        return evidence_bag
