from typing import Dict
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase, MaximumRiskEvidence, CapitalAllocationEvidence

class MaximumRiskStage(ISizingMetricStage):
    @property
    def stage_name(self) -> str:
        return "maximum_risk"
        
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> MaximumRiskEvidence:
        # Consume from previous stage
        alloc_evidence = previous_results.get("capital_allocation")
        if not isinstance(alloc_evidence, CapitalAllocationEvidence):
            raise ValueError("MaximumRiskStage requires CapitalAllocationEvidence from previous stage.")
            
        max_risk_pct = context.allocation_configuration.get("max_risk_pct", 0.02)
        allocated_capital = alloc_evidence.allocated_capital
        max_risk_amount = allocated_capital * max_risk_pct
        
        return MaximumRiskEvidence(
            metric_id="maximum_risk",
            metric_version="1.0.0",
            source_snapshot_id=context.risk_evaluation_snapshot.snapshot_id,
            calculation_metadata={"max_risk_pct": max_risk_pct},
            allocated_capital=allocated_capital,
            max_risk_percentage=max_risk_pct,
            max_risk_amount=max_risk_amount
        )
