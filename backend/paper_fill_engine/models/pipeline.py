from pydantic import BaseModel
from typing import List, Dict

class PipelineDiagnostics(BaseModel):
    validation_errors: List[str] = []
    warnings: List[str] = []

class PipelineTelemetry(BaseModel):
    execution_duration_ms: float = 0.0
    stage_timings: Dict[str, float] = {}
