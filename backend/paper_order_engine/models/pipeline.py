from pydantic import BaseModel
from typing import List

class PipelineDiagnostics(BaseModel):
    warnings: List[str] = []
    structural_validation_warnings: List[str] = []
    consistency_validation_warnings: List[str] = []

class PipelineTelemetry(BaseModel):
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
