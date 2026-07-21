from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import PortfolioDecisionEvidence, StageStatus

class PortfolioConstraintStage(IRiskDecisionStage):
    """
    Evaluates global portfolio constraints (e.g., max portfolio open risk overall valid).
    """
    async def evaluate(self, context: RiskDecisionContext) -> PortfolioDecisionEvidence:
        port_ev = context.portfolio_risk_snapshot.report.portfolio_exposure_evidence
        
        status = StageStatus.PASS if getattr(port_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = port_ev.metric_id if port_ev else "none"
        
        return PortfolioDecisionEvidence(
            metric_id=f"port_con_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="PortfolioConstraintStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
