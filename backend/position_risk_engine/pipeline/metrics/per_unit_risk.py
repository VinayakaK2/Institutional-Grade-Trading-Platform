from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import PerUnitRiskEvidence

class PerUnitRiskMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "per_unit_risk"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> PerUnitRiskEvidence:
        # For simple instruments, 1 unit = 1 x distance. 
        # Future configurations might use instrument_metadata to adjust for multiplier/pip value.
        multiplier = context.instrument_metadata.get("multiplier", 1.0)
        dist = abs(context.entry_price - context.initial_stop_loss)
        
        per_unit = dist * multiplier
        
        return PerUnitRiskEvidence(
            calculation_method="abs(entry - stop_loss) * multiplier",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            entry_price=context.entry_price,
            stop_loss=context.initial_stop_loss,
            risk_per_unit=per_unit
        )
