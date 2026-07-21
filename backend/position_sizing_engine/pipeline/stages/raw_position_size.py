from typing import Dict
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase, MaximumRiskEvidence, RawPositionSizeEvidence

class RawPositionSizeStage(ISizingMetricStage):
    @property
    def stage_name(self) -> str:
        return "raw_position_size"
        
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> RawPositionSizeEvidence:
        max_risk_evidence = previous_results.get("maximum_risk")
        if not isinstance(max_risk_evidence, MaximumRiskEvidence):
            raise ValueError("RawPositionSizeStage requires MaximumRiskEvidence.")
            
        per_unit_risk_ev = context.risk_evaluation_snapshot.report.per_unit_risk_evidence
        if not per_unit_risk_ev:
            raise ValueError("Risk Evaluation Snapshot is missing per_unit_risk_evidence.")
            
        risk_per_unit = per_unit_risk_ev.risk_per_unit
        max_risk_amount = max_risk_evidence.max_risk_amount
        
        raw_size = max_risk_amount / risk_per_unit if risk_per_unit > 0 else 0.0
        
        return RawPositionSizeEvidence(
            metric_id="raw_position_size",
            metric_version="1.0.0",
            source_snapshot_id=context.risk_evaluation_snapshot.snapshot_id,
            calculation_metadata={"method": "max_risk / risk_per_unit"},
            max_risk_amount=max_risk_amount,
            risk_per_unit=risk_per_unit,
            raw_position_size=raw_size
        )
