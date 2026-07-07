"""
Watchlist Certification Models
==============================

Immutable data models representing the certification process.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class BusinessMetadata(BaseModel):
    """
    Deterministic metadata used to uniquely identify the business logic version.
    Must never contain runtime-dependent values.
    """
    model_config = ConfigDict(frozen=True)

    pipeline_version: str = Field(..., description="The semantic version of the pipeline.")
    config_hash: str = Field(..., description="The configuration hash representing the pipeline's settings.")
    business_fingerprint_version: int = Field(..., description="The algorithm version used for business fingerprints.")


class ExecutionMetadata(BaseModel):
    """
    Runtime-specific metadata that will change between executions.
    """
    model_config = ConfigDict(frozen=True)

    execution_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    python_version: str
    execution_time_ms: float
    memory_usage_mb: Optional[float] = None
    environment_info: Dict[str, str] = Field(default_factory=dict)


class CertificationStageResult(BaseModel):
    """
    Immutable record of a certification stage's execution.
    """
    model_config = ConfigDict(frozen=True)

    stage_name: str
    passed: bool
    execution_time_ms: float
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class CertificationReport(BaseModel):
    """
    The final immutable aggregation of all certification stages.
    """
    model_config = ConfigDict(frozen=True)

    passed: bool
    business_metadata: BusinessMetadata
    execution_metadata: ExecutionMetadata
    stage_results: List[CertificationStageResult]


class CertificationContext:
    """
    The shared context passed between stages.
    Holds generators and testing dependencies.
    """
    def __init__(self) -> None:
        # Initialized without arguments to allow stages to access it easily
        self.dataset_generator: Any = None  # Will be injected by the engine
        self.build_engine: Any = None       # Factory method injected by the engine
        self.stage_results: List[CertificationStageResult] = []
        
    def add_result(self, result: CertificationStageResult) -> None:
        """Appends a new result. Previous results are never mutated."""
        self.stage_results.append(result)
