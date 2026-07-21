from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import StopLossEvidence

class StopLossMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "stop_loss"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> StopLossEvidence:
        return StopLossEvidence(
            calculation_method="direct-extraction",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            stop_loss=context.initial_stop_loss
        )
