from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field

class CertificationPhaseEnum(str, Enum):
    FOUNDATION = "FOUNDATION"
    DETECTION = "DETECTION"
    QUALITY = "QUALITY"
    LIFECYCLE = "LIFECYCLE"
    OPTIMIZATION = "OPTIMIZATION"

class CertificationPhaseResult(BaseModel):
    """
    Result of verifying a specific phase of the pipeline.
    """
    phase: CertificationPhaseEnum = Field(description="The phase being certified")
    success: bool = Field(description="Whether the verification passed")
    execution_time_ms: float = Field(description="Execution time in milliseconds")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metrics gathered during phase certification")
    error_message: Optional[str] = Field(default=None, description="Reason for failure, if any")

    model_config = ConfigDict(frozen=True)

class CertificationSummary(BaseModel):
    """
    Rollup summary of the entire certification run.
    """
    is_certified: bool = Field(description="Whether the entire engine passed certification")
    total_execution_time_ms: float = Field(description="Total time taken for certification")
    phase_results: List[CertificationPhaseResult] = Field(default_factory=list, description="Results for each phase")

    model_config = ConfigDict(frozen=True)

class CertificationReport(BaseModel):
    """
    Immutable root entity representing the result of a certification run.
    """
    report_id: str = Field(description="Deterministic ID for this certification report")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When this certification occurred")
    dataset_metadata: Dict[str, Any] = Field(description="Metadata about the synthetic dataset used")
    environment_details: Dict[str, Any] = Field(description="Details about the environment (e.g., framework versions)")
    summary: CertificationSummary = Field(description="The certification summary")

    model_config = ConfigDict(frozen=True)

class CertificationContext(BaseModel):
    """
    Settings to guide the certification run.
    """
    stress_test_sizes: List[int] = Field(default_factory=lambda: [100, 500, 1000], description="Batch sizes to use for stress verification")
    run_performance_benchmarks: bool = Field(default=True, description="Whether to execute the performance verification")
    fail_fast: bool = Field(default=False, description="Whether to stop on first verification failure")
    
    benchmark_iterations: int = Field(default=1, description="Number of iterations for performance benchmarking")
    random_seed: int = Field(default=42, description="Seed for deterministic dataset generation")
    environment_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the host environment")

    model_config = ConfigDict(frozen=True)
