from typing import Dict
from backend.position_sizing_engine.pipeline.contracts import ISizingMetricStage
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase, RawPositionSizeEvidence, RoundLotEvidence
from backend.position_sizing_engine.pipeline.policies.registry import RoundLotPolicyRegistry

class RoundLotAdjustmentStage(ISizingMetricStage):
    def __init__(self, registry: RoundLotPolicyRegistry):
        self._registry = registry

    @property
    def stage_name(self) -> str:
        return "round_lot_adjustment"
        
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> RoundLotEvidence:
        raw_size_evidence = previous_results.get("raw_position_size")
        if not isinstance(raw_size_evidence, RawPositionSizeEvidence):
            raise ValueError("RoundLotAdjustmentStage requires RawPositionSizeEvidence.")
            
        raw_size = raw_size_evidence.raw_position_size
        asset_type = context.instrument_metadata.get("asset_type", "equity")
        policy = self._registry.resolve(asset_type)
        
        rounded_size = policy.apply(raw_size)
        
        return RoundLotEvidence(
            metric_id="round_lot_adjustment",
            metric_version="1.0.0",
            source_snapshot_id=context.risk_evaluation_snapshot.snapshot_id,
            calculation_metadata={"policy": policy.policy_name},
            raw_position_size=raw_size,
            rounded_position_size=rounded_size,
            rounding_policy=policy.policy_name
        )
