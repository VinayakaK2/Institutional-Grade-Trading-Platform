from typing import List, Dict
from pydantic import BaseModel, Field
from backend.historical_data.models.raw import RawCandle

class CleaningResult(BaseModel):
    """
    Structured output from the Cleaning Engine.
    """
    valid_records: List[RawCandle] = Field(default_factory=list)
    cleaned_records: List[RawCandle] = Field(default_factory=list)
    rejected_records: List[RawCandle] = Field(default_factory=list)
    
    cleaning_actions: List[str] = Field(default_factory=list)
    statistics: Dict[str, int] = Field(default_factory=dict)
    duration_seconds: float = 0.0
