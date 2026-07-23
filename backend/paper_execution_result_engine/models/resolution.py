from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat, ConfigDict

class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class ExecutionSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    requested_quantity: StrictInt
    filled_quantity: StrictInt
    remaining_quantity: StrictInt
    fill_count: StrictInt
    average_fill_price: Optional[StrictFloat]
    
    execution_cost: StrictFloat
    total_slippage: StrictFloat
    total_market_impact: StrictFloat
    total_spread_cost: StrictFloat
    
    execution_status: ExecutionStatus

class ExecutionEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    event_id: StrictStr
    event_type: StrictStr
    timestamp: StrictStr
    sequence_number: StrictInt
    details: dict

class ExecutionTimeline(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    events: List[ExecutionEvent]
