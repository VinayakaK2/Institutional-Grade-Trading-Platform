from enum import Enum
from pydantic import BaseModel, ConfigDict
from backend.support_resistance_engine.models.zone import SwingPoint

class StructureType(str, Enum):
    HH = "HH"  # Higher High
    HL = "HL"  # Higher Low
    LH = "LH"  # Lower High
    LL = "LL"  # Lower Low

class MarketStructurePoint(BaseModel):
    """
    Wraps a SwingPoint with its classified market structure type.
    """
    model_config = ConfigDict(frozen=True)
    
    id: str
    swing_point: SwingPoint
    type: StructureType
