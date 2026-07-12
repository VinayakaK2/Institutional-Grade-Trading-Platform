import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.trade_validation_engine.models.context import TradeValidationExecutionContext

class TradeValidationRequest(BaseModel):
    """
    Input request for validating a trade.
    Contains the context and any necessary configurations to execute the pipeline.
    """
    context: TradeValidationExecutionContext = Field(description="The execution context")
    request_id: str = Field(default_factory=lambda: hashlib.sha256(str(datetime.now().timestamp()).encode('utf-8')).hexdigest(), description="Unique identifier for the request")
    
    model_config = {"frozen": True}


class ValidationStageResult(BaseModel):
    """
    Result of a single validation stage in the pipeline.
    """
    stage_name: str = Field(description="Name of the validation stage")
    success: bool = Field(description="Whether the stage passed validation")
    error_message: Optional[str] = Field(default=None, description="Error message if validation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata from the stage execution")
    
    model_config = {"frozen": True}


class ValidationPipelineResult(BaseModel):
    """
    Aggregate result of all executed validation stages.
    """
    success: bool = Field(description="Whether all executed stages passed")
    stage_results: List[ValidationStageResult] = Field(default_factory=list, description="Results of individual stages")
    
    model_config = {"frozen": True}


class TradeValidationMetadata(BaseModel):
    """
    Metadata surrounding the validation execution.
    """
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the snapshot was assembled")
    execution_duration_ms: int = Field(default=0, description="Duration of pipeline execution in milliseconds")
    
    model_config = {"frozen": True}


class TradeValidationSnapshot(BaseModel):
    """
    Immutable root entity representing a complete Trade Validation result.
    """
    snapshot_id: str = Field(description="Deterministic ID for this snapshot")
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    
    pipeline_result: ValidationPipelineResult = Field(description="Result of the validation pipeline")
    context: TradeValidationExecutionContext = Field(description="Execution context used to generate this snapshot")
    metadata: TradeValidationMetadata = Field(description="Execution metadata")
    
    @classmethod
    def generate_id(cls, symbol: str, timeframe: str, dataset_version: int, wl_version: int, t_version: int, c_version: int, lg_version: int) -> str:
        """
        Generates a deterministic Snapshot ID from stable business inputs.
        """
        payload = f"{symbol}_{timeframe}_{dataset_version}_{wl_version}_{t_version}_{c_version}_{lg_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    model_config = {"frozen": True}
