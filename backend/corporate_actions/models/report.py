from typing import List, Dict
from pydantic import BaseModel, Field

class PipelineReport(BaseModel):
    """Report generated after a corporate actions pipeline run."""
    total_actions: int = Field(default=0, description="Total number of actions processed")
    applied_actions: int = Field(default=0, description="Number of actions successfully applied/validated")
    rejected_actions: int = Field(default=0, description="Number of actions rejected")
    symbols_affected: int = Field(default=0, description="Unique symbols affected by the run")
    processing_duration_seconds: float = Field(default=0.0, description="Time taken to process in seconds")
    validation_errors: List[Dict[str, str]] = Field(default_factory=list, description="List of errors encountered during validation")
