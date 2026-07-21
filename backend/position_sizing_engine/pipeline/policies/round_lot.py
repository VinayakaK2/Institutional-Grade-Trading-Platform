import math
from backend.position_sizing_engine.pipeline.policies.contracts import IRoundLotPolicy

class EquityRoundLotPolicy(IRoundLotPolicy):
    """
    Floors the raw position size to the nearest whole number (e.g. integer shares).
    """
    def apply(self, raw_size: float) -> float:
        return math.floor(raw_size)
        
    @property
    def policy_name(self) -> str:
        return "EquityRoundLotPolicy (Floor to Integer)"

class FractionalAssetPolicy(IRoundLotPolicy):
    """
    Allows fractional position sizes, rounding to a specified number of decimal places.
    """
    def __init__(self, decimal_places: int = 4):
        self._decimal_places = decimal_places
        
    def apply(self, raw_size: float) -> float:
        # Simple rounding for fractional assets (crypto, fractional shares)
        return round(raw_size, self._decimal_places)
        
    @property
    def policy_name(self) -> str:
        return f"FractionalAssetPolicy (Round to {self._decimal_places} decimals)"
