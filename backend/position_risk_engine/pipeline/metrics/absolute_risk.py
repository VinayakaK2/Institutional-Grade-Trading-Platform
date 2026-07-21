from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import AbsoluteRiskEvidence

class AbsoluteRiskMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "absolute_risk"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> AbsoluteRiskEvidence:
        dist = abs(context.entry_price - context.initial_stop_loss)
        return AbsoluteRiskEvidence(
            calculation_method="abs(entry - stop_loss)",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            entry_price=context.entry_price,
            stop_loss=context.initial_stop_loss,
            risk_distance=dist,
            absolute_risk=dist # For basic instruments, absolute risk distance is the same. Later phases might multiply by point value
        )
