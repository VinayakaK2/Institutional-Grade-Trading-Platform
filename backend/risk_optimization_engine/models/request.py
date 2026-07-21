from pydantic import BaseModel, Field
from typing import Any
from backend.risk_optimization_engine.models.fingerprint import BusinessFingerprint

class OptimizationRequest(BaseModel):
    """
    Request object encapsulating the inputs to the risk pipeline and optimization configs.
    """
    pipeline_version: str = Field(description="Version of the pipeline to run")
    fingerprint: BusinessFingerprint = Field(description="Deterministic fingerprint of the request")
    raw_input: Any = Field(description="The actual input object passed to the pipeline")
    
    model_config = {"frozen": True}
