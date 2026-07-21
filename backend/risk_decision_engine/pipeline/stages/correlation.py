from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import CorrelationDecisionEvidence, StageStatus

class CorrelationStage(IRiskDecisionStage):
    """
    Evaluates correlation constraints across the portfolio.
    """
    async def evaluate(self, context: RiskDecisionContext) -> CorrelationDecisionEvidence:
        corr_ev = context.portfolio_risk_snapshot.report.correlation_evidence
        
        status = StageStatus.PASS if getattr(corr_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = corr_ev.metric_id if corr_ev else "none"
        
        return CorrelationDecisionEvidence(
            metric_id=f"corr_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="CorrelationStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
