from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, PortfolioExposureEvidence

class MaximumPortfolioRiskStage(IPortfolioRiskStage):
    """
    Validates if the total portfolio risk stays within global account limits 
    if this new position is added.
    """
    @property
    def stage_name(self) -> str:
        return "portfolio_exposure"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> PortfolioExposureEvidence:
        
        current_risk = provider.get_total_open_risk()
        max_risk_evidence = context.position_sizing_snapshot.report.maximum_risk_evidence
        if max_risk_evidence is None:
            raise ValueError("Maximum risk evidence is required.")
        new_risk = max_risk_evidence.max_risk_amount
        projected = current_risk + new_risk
        
        # Max limit could come from context.configuration, or a global variable in metadata
        limit = context.metadata.get("max_portfolio_risk_limit", 10000.0) # default fallback
        
        is_valid = projected <= limit
        
        return PortfolioExposureEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": limit, "formula": "current + new_risk <= limit"},
            current_portfolio_risk=current_risk,
            new_position_risk=new_risk,
            projected_portfolio_risk=projected,
            max_portfolio_risk_limit=limit,
            is_valid=is_valid
        )
