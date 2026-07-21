from typing import Dict
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase, CapitalAllocationEvidence

class CapitalAllocationStage(ISizingMetricStage):
    @property
    def stage_name(self) -> str:
        return "capital_allocation"
        
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> CapitalAllocationEvidence:
        allocation_pct = context.allocation_configuration.get("allocation_pct", 1.0)
        allocated_capital = context.available_capital * allocation_pct
        
        return CapitalAllocationEvidence(
            metric_id="capital_allocation",
            metric_version="1.0.0",
            source_snapshot_id=context.risk_evaluation_snapshot.snapshot_id,
            calculation_metadata={"allocation_pct": allocation_pct},
            available_capital=context.available_capital,
            allocation_percentage=allocation_pct,
            allocated_capital=allocated_capital
        )
