from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, DailyRiskEvidence

class DailyRiskLimitStage(IPortfolioRiskStage):
    """
    Validates daily risk loss budgets.
    """
    @property
    def stage_name(self) -> str:
        return "daily_risk"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> DailyRiskEvidence:
        
        current_loss = provider.get_daily_risk()
        max_risk_evidence = context.position_sizing_snapshot.report.maximum_risk_evidence
        if max_risk_evidence is None:
            raise ValueError("Maximum risk evidence is required.")
        new_risk = max_risk_evidence.max_risk_amount
        projected = current_loss + new_risk
        
        limit = context.metadata.get("max_daily_loss_limit", 2000.0)
        
        is_valid = projected <= limit
        
        return DailyRiskEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": limit},
            current_daily_loss=current_loss,
            new_position_risk=new_risk,
            projected_daily_risk=projected,
            max_daily_loss_limit=limit,
            is_valid=is_valid
        )
