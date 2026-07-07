from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class CertificationMode(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    INTEGRATION = "INTEGRATION"

class UniverseCertificationConfiguration(BaseModel):
    """
    Configuration for the certification engine.
    """
    mode: CertificationMode = CertificationMode.DETERMINISTIC
    stress_test_sizes: List[int] = Field(default_factory=lambda: [100, 500, 1000])
    stress_test_repeated_runs: int = 100

class PerformanceMetrics(BaseModel):
    """
    Performance measurements captured during certification.
    Informational only.
    """
    execution_time_ms: float = 0.0
    peak_memory_usage_mb: float = 0.0
    cpu_time_ms: float = 0.0
    symbols_per_second: float = 0.0
    stage_execution_breakdown: Dict[str, float] = Field(default_factory=dict)

class CertificationReport(BaseModel):
    """
    Immutable resulting artifact of the Certification Engine.
    
    CERTIFICATION COMPATIBILITY CONTRACT:
    If the Universe pipeline schema changes in the future, CertificationReport versions 
    are inextricably tied to the following fields to preserve historical reproducibility:
    - `pipeline_version`: Tracks structural changes to the Universe pipeline stages.
    - `config_hash`: Tracks changes to execution configurations.
    - `business_fingerprint_version`: Tracks structural changes to business logic and diff detection.
    """
    model_config = ConfigDict(frozen=True)

    certification_id: str
    pipeline_version: str
    config_hash: str
    business_fingerprint_version: str
    git_commit_hash: Optional[str] = None
    created_at: datetime
    
    configuration_snapshot: UniverseCertificationConfiguration
    
    # PASS/FAIL for overall and detailed sections
    functional_passed: bool
    determinism_passed: bool
    integrity_passed: bool
    stress_passed: bool
    is_certified: bool
    
    test_results: Dict[str, Any]
    determinism_results: Dict[str, Any]
    performance_metrics: PerformanceMetrics

class UniverseCertificationContext(BaseModel):
    """
    Mutable context used during the certification pipeline execution.
    """
    run_id: str
    config: UniverseCertificationConfiguration
    
    # Capturing state as we execute stages
    functional_passed: bool = True
    determinism_passed: bool = True
    integrity_passed: bool = True
    stress_passed: bool = True
    is_certified: bool = False
    
    test_results: Dict[str, Any] = Field(default_factory=dict)
    determinism_results: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    
    started_at: datetime

class UniverseCertificationResult(BaseModel):
    """
    Wrapper for the output of the Certification Engine.
    """
    model_config = ConfigDict(frozen=True)
    report: CertificationReport
