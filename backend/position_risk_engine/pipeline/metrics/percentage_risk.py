from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import PercentageRiskEvidence

class PercentageRiskMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "percentage_risk"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> PercentageRiskEvidence:
        dist = abs(context.entry_price - context.initial_stop_loss)
        pct = dist / context.entry_price if context.entry_price != 0 else 0.0
        
        return PercentageRiskEvidence(
            calculation_method="abs(entry - stop_loss) / entry",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            entry_price=context.entry_price,
            stop_loss=context.initial_stop_loss,
            percentage_risk=pct
        )
