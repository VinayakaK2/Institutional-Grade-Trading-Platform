from typing import Dict
from backend.portfolio_risk_engine.pipeline.contracts import IPortfolioRiskStage
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.models.evidence import PortfolioEvidenceBase, CorrelationEvidence

class CorrelationExposureStage(IPortfolioRiskStage):
    """
    Validates correlation exposure, identifying if the portfolio contains 
    too many highly correlated assets to the new symbol.
    """
    @property
    def stage_name(self) -> str:
        return "correlation_exposure"
        
    async def calculate(
        self, 
        context: PortfolioRiskContext, 
        provider: IPortfolioSnapshotProvider,
        previous_evidence: Dict[str, PortfolioEvidenceBase]
    ) -> CorrelationEvidence:
        
        symbol = context.risk_evaluation_snapshot.context.symbol
        correlation_matrix = provider.get_correlation_matrix()
        
        max_correlation = context.metadata.get("max_correlation_limit", 0.8)
        
        symbol_correlations = correlation_matrix.get(symbol, {})
        
        highly_correlated = {k: v for k, v in symbol_correlations.items() if v >= max_correlation}
        
        # Validity: Are there fewer than 3 highly correlated assets?
        is_valid = len(highly_correlated) < 3
        
        return CorrelationEvidence(
            metric_id=self.stage_name,
            metric_version="1.0.0",
            source_snapshot_id=context.position_sizing_snapshot.snapshot_id,
            calculation_metadata={"limit": max_correlation, "highly_correlated_count": len(highly_correlated)},
            symbol=symbol,
            highly_correlated_assets=highly_correlated,
            max_correlation_limit=max_correlation,
            is_valid=is_valid
        )
