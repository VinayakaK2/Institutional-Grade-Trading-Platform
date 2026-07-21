from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import SectorDecisionEvidence, StageStatus

class SectorExposureStage(IRiskDecisionStage):
    """
    Evaluates if the position exceeds sector concentration limits.
    """
    async def evaluate(self, context: RiskDecisionContext) -> SectorDecisionEvidence:
        sector_ev = context.portfolio_risk_snapshot.report.sector_exposure_evidence
        
        status = StageStatus.PASS if getattr(sector_ev, "is_valid", True) else StageStatus.FAIL
        source_metric_id = sector_ev.metric_id if sector_ev else "none"
        
        return SectorDecisionEvidence(
            metric_id=f"sec_exp_{context.portfolio_risk_snapshot.snapshot_id}",
            stage_name="SectorExposureStage",
            status=status,
            calculation_metadata={"source_metric_id": source_metric_id}
        )
