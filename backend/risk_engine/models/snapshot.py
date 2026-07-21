from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.risk_engine.models.context import RiskExecutionContext

class RiskMetadata(BaseModel):
    """
    Immutable metadata associated with the risk snapshot.
    """
    pipeline_version: str = Field(description="Version of the pipeline used")
    execution_duration_ms: int = Field(description="Total execution time in milliseconds")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution info")
    
    model_config = {"frozen": True}

class ValidationResult(BaseModel):
    """
    Result from a validation layer execution.
    """
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation error messages, if any")
    
    model_config = {"frozen": True}

class PipelineResult(BaseModel):
    """
    Result of the pipeline execution.
    """
    success: bool = Field(description="Whether the pipeline executed successfully")
    stage_results: Dict[str, Any] = Field(default_factory=dict, description="Results from individual pipeline stages")
    
    model_config = {"frozen": True}

class RiskSnapshot(BaseModel):
    """
    Immutable snapshot containing the finalized risk structure.
    No business logic fields yet, serves as a foundation.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the snapshot")
    context: RiskExecutionContext = Field(description="Execution context that generated this snapshot")
    pipeline_result: PipelineResult = Field(description="Result of the pipeline execution")
    validation_status: ValidationResult = Field(description="Aggregate validation status")
    metadata: RiskMetadata = Field(description="Associated metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    model_config = {"frozen": True}
