from pydantic import BaseModel, Field, StrictStr, StrictInt, StrictFloat, ConfigDict

class FillEvent(BaseModel):
    """
    Immutable representation of a single simulated fill.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    fill_id: StrictStr = Field(..., description="Unique identifier for the fill event")
    quantity: StrictInt = Field(..., description="Quantity filled in this event")
    price: StrictFloat = Field(..., description="Price at which this quantity was filled")
    timestamp: StrictStr = Field(..., description="ISO 8601 timestamp of the fill event")
    sequence_number: StrictInt = Field(..., description="1-indexed sequence number of this fill")
    remaining_quantity_after_fill: StrictInt = Field(..., description="Quantity remaining on the order after this fill")
