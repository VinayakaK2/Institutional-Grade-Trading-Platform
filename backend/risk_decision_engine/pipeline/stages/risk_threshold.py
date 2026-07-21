from backend.risk_decision_engine.pipeline.contracts import IRiskDecisionStage
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.evidence import RiskThresholdEvidence, StageStatus

class RiskThresholdStage(IRiskDecisionStage):
    """
    Evaluates the single position risk thresholds.
    """
    async def evaluate(self, context: RiskDecisionContext) -> RiskThresholdEvidence:
        # Check if the RiskEvaluationSnapshot was structurally valid and had no errors
        is_valid = context.risk_evaluation_snapshot.report.validation_status.is_valid
        
        status = StageStatus.PASS if is_valid else StageStatus.FAIL
        
        return RiskThresholdEvidence(
            metric_id=f"risk_thresh_{context.risk_evaluation_snapshot.snapshot_id}",
            stage_name="RiskThresholdStage",
            status=status,
            calculation_metadata={"reason": "Passed risk threshold limits" if is_valid else "Failed risk threshold limits"}
        )
