from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, PositionExposureEvidence

class PositionExposureStage(IPortfolioRiskStage):
    """
    Validates single symbol concentration limits.
    """
    @property
    def stage_name(self) -> str:
        return "position_exposure"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> PositionExposureEvidence:
        
        symbol = context.risk_evaluation_snapshot.context.symbol
        
        current_exposure = provider.get_position_exposure(symbol)
        
        # We define exposure in this context as total raw capital allocated
        capital_evidence = context.position_sizing_snapshot.report.capital_allocation_evidence
        if capital_evidence is None:
            raise ValueError("Capital Allocation Evidence is required.")
        new_exposure = capital_evidence.allocated_capital
        
        projected = current_exposure + new_exposure
        
        limit = context.metadata.get("max_single_position_exposure_limit", 50000.0)
        
        is_valid = projected <= limit
        
        return PositionExposureEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": limit, "symbol": symbol},
            symbol=symbol,
            current_position_exposure=current_exposure,
            new_position_exposure=new_exposure,
            projected_position_exposure=projected,
            max_position_exposure_limit=limit,
            is_valid=is_valid
        )
