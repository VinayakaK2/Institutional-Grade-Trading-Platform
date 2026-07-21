from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import DistanceEvidence

class StopLossDistanceMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "distance"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> DistanceEvidence:
        dist = abs(context.entry_price - context.initial_stop_loss)
        return DistanceEvidence(
            calculation_method="abs(entry - stop_loss)",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            entry_price=context.entry_price,
            stop_loss=context.initial_stop_loss,
            risk_distance=dist
        )
