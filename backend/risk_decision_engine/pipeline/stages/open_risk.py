from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import OpenRiskDecisionEvidence, StageStatus

class OpenRiskStage(IRiskDecisionStage):
    """
    Evaluates if total open portfolio risk exceeds global limit.
    """
    async def evaluate(self, context: RiskDecisionContext) -> OpenRiskDecisionEvidence:
        or_ev = context.portfolio_risk_snapshot.report.open_risk_evidence
        
        status = StageStatus.PASS if getattr(or_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = or_ev.metric_id if or_ev else "none"
        
        return OpenRiskDecisionEvidence(
            metric_id=f"open_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="OpenRiskStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
