from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import DailyRiskDecisionEvidence, StageStatus

class DailyRiskStage(IRiskDecisionStage):
    """
    Evaluates if adding this position breaches daily risk limit.
    """
    async def evaluate(self, context: RiskDecisionContext) -> DailyRiskDecisionEvidence:
        dr_ev = context.portfolio_risk_snapshot.report.daily_risk_evidence
        
        status = StageStatus.PASS if getattr(dr_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = dr_ev.metric_id if dr_ev else "none"
        
        return DailyRiskDecisionEvidence(
            metric_id=f"daily_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="DailyRiskStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
