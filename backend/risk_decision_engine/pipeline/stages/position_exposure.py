from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import ExposureDecisionEvidence, StageStatus

class PositionExposureStage(IRiskDecisionStage):
    """
    Evaluates if the position exceeds max exposure limits.
    """
    async def evaluate(self, context: RiskDecisionContext) -> ExposureDecisionEvidence:
        pos_ev = context.portfolio_risk_snapshot.report.position_exposure_evidence
        
        status = StageStatus.PASS if getattr(pos_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = pos_ev.metric_id if pos_ev else "none"
        
        return ExposureDecisionEvidence(
            metric_id=f"pos_exp_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="PositionExposureStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
