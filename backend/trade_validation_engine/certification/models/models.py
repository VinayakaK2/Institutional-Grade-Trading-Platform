from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class StageResult(BaseModel):
    """
    Immutable result of a single certification stage.
    """
    stage_name: str = Field(description="Name of the certification stage")
    status: str = Field(description="Status: PASS, FAIL, SKIP")
    duration_ms: int = Field(description="Execution duration in milliseconds")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Stage-specific telemetry (e.g., peak memory, speedup)")
    evidence_path: Optional[str] = Field(default=None, description="Path to persisted raw evidence JSON")
    error_message: Optional[str] = Field(default=None, description="Error details if the stage failed")
    
    model_config = {"frozen": True}

class QualityGateStatus(BaseModel):
    """
    Status of automated quality gates.
    """
    ruff_status: str = Field(description="Status of ruff linter")
    mypy_status: str = Field(description="Status of mypy type checker")
    bandit_status: str = Field(description="Status of bandit security analysis")
    pytest_status: str = Field(description="Status of functional tests")
    coverage_percentage: float = Field(description="Code coverage percentage")
    
    model_config = {"frozen": True}

class CertificationReport(BaseModel):
    """
    Exhaustive, immutable audit document proving completion of Phase 10.6 certification.
    """
    certification_id: str = Field(description="Unique deterministic identifier for this report")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Certification completion time")
    
    # Environment Metadata
    platform_info: str = Field(description="OS / Platform identifier")
    python_version: str = Field(description="Python version")
    git_commit: Optional[str] = Field(default=None, description="Git commit hash if available")
    
    # Verification Targets
    dataset_version: str = Field(description="Golden Dataset version")
    dataset_seed: int = Field(description="Seed used for procedural generation")
    configuration_hash: str = Field(description="Hash of the used configuration")
    business_fingerprint_version: str = Field(description="Version of fingerprinting algorithm")
    
    # Process Metrics
    snapshot_count: int = Field(description="Total snapshots evaluated during stress tests")
    parallel_workers: int = Field(description="Workers used during parallel verifications")
    total_execution_time_ms: int = Field(description="Total time spent across all stages")
    peak_memory_mb: float = Field(description="Maximum observed memory during testing")
    
    # Sub-results
    stage_results: List[StageResult] = Field(description="Results of each certification stage")
    quality_gates: QualityGateStatus = Field(description="Automated CI verification checks")
    
    overall_result: str = Field(description="Final certification status: CERTIFIED, FAILED, INCOMPLETE")
    
    model_config = {"frozen": True}
