from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, SectorExposureEvidence

class SectorExposureStage(IPortfolioRiskStage):
    """
    Validates sector concentration limits.
    """
    @property
    def stage_name(self) -> str:
        return "sector_exposure"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> SectorExposureEvidence:
        
        sector = context.position_sizing_snapshot.context.instrument_metadata.get("sector", "unknown")
        
        current_exposure = provider.get_sector_exposure(sector)
        capital_evidence = context.position_sizing_snapshot.report.capital_allocation_evidence
        if capital_evidence is None:
            raise ValueError("Capital Allocation Evidence is required.")
        new_exposure = capital_evidence.allocated_capital
        projected = current_exposure + new_exposure
        
        limit = context.metadata.get("max_sector_exposure_limit", 150000.0)
        
        is_valid = projected <= limit
        
        return SectorExposureEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": limit, "sector": sector},
            sector=sector,
            current_sector_exposure=current_exposure,
            new_position_exposure=new_exposure,
            projected_sector_exposure=projected,
            max_sector_exposure_limit=limit,
            is_valid=is_valid
        )
