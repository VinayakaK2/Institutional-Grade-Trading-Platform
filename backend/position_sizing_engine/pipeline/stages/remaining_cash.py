from typing import Dict
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase, CapitalAllocationEvidence, RoundLotEvidence, RemainingCashEvidence

class RemainingCashStage(ISizingMetricStage):
    @property
    def stage_name(self) -> str:
        return "remaining_cash"
        
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> RemainingCashEvidence:
        alloc_evidence = previous_results.get("capital_allocation")
        if not isinstance(alloc_evidence, CapitalAllocationEvidence):
            raise ValueError("RemainingCashStage requires CapitalAllocationEvidence.")
            
        round_lot_evidence = previous_results.get("round_lot_adjustment")
        if not isinstance(round_lot_evidence, RoundLotEvidence):
            raise ValueError("RemainingCashStage requires RoundLotEvidence.")
            
        allocated_capital = alloc_evidence.allocated_capital
        rounded_size = round_lot_evidence.rounded_position_size
        entry_price = context.risk_evaluation_snapshot.report.entry_evidence.entry_price if context.risk_evaluation_snapshot.report.entry_evidence else 0.0
        
        # Base assumption: cost = size * entry_price. 
        # Multipliers/margins would alter this in real asset classes, but for simple evaluation:
        position_cost = rounded_size * entry_price
        remaining_cash = allocated_capital - position_cost
        
        return RemainingCashEvidence(
            metric_id="remaining_cash",
            metric_version="1.0.0",
            source_snapshot_id=context.risk_evaluation_snapshot.snapshot_id,
            calculation_metadata={"method": "allocated - (size * entry)"},
            allocated_capital=allocated_capital,
            position_cost=position_cost,
            remaining_cash=remaining_cash
        )
