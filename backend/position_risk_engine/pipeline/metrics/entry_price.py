from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.evidence import EntryEvidence

class EntryPriceMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str:
        return "entry_price"
        
    async def calculate(self, context: PositionRiskEvaluationContext) -> EntryEvidence:
        return EntryEvidence(
            calculation_method="direct-extraction",
            source_snapshot_id=context.trade_decision_snapshot_version,
            engine_version=context.configuration.pipeline_version,
            entry_price=context.entry_price
        )
