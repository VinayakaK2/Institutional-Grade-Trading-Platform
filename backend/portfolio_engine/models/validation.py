from pydantic import BaseModel, Field
from typing import Optional

class ValidationResult(BaseModel):
    """
    Structured outcome of a validation step.
    Engine flow control is determined by this result, not exceptions.
    """
    is_valid: bool = Field(description="True if validation passed")
    reason: Optional[str] = Field(default=None, description="Detailed reason for validation failure")
    
    model_config = {"frozen": True}
