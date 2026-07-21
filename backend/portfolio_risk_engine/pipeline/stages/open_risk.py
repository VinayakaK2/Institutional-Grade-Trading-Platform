from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, OpenRiskEvidence

class OpenRiskLimitStage(IPortfolioRiskStage):
    """
    Validates open risk count (active trades count limit).
    """
    @property
    def stage_name(self) -> str:
        return "open_risk"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> OpenRiskEvidence:
        
        current_open = provider.get_open_positions_count()
        projected_open = current_open + 1
        
        limit = context.metadata.get("max_open_positions_limit", 15)
        
        is_valid = projected_open <= limit
        
        return OpenRiskEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": limit},
            current_open_risk=float(current_open),
            new_position_risk=1.0,
            projected_open_risk=float(projected_open),
            max_open_risk_limit=float(limit),
            is_valid=is_valid
        )
