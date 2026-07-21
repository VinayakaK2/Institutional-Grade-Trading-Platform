from pydantic import BaseModel, Field
from typing import Any, Dict

class VerificationRecord(BaseModel):
    """
    Standardized response format for verification checks.
    """
    certifier_name: str = Field(description="Name of the certifier that produced this record")
    status: str = Field(description="PASS or FAIL")
    evidence: str = Field(description="Summary of the evidence collected")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Detailed metrics collected during the run")
    
    model_config = {"frozen": True}
