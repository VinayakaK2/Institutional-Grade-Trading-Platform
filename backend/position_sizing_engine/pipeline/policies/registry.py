from typing import Dict
from backend.position_sizing_engine.pipeline.policies.contracts import IRoundLotPolicy

class RoundLotPolicyRegistry:
    """
    Registry for resolving rounding policies dynamically based on asset type.
    """
    def __init__(self):
        self._policies: Dict[str, IRoundLotPolicy] = {}
        
    def register(self, asset_type: str, policy: IRoundLotPolicy) -> None:
        self._policies[asset_type.lower()] = policy
        
    def resolve(self, asset_type: str) -> IRoundLotPolicy:
        policy = self._policies.get(asset_type.lower())
        if not policy:
            raise ValueError(f"No RoundLotPolicy registered for asset type: {asset_type}")
        return policy
