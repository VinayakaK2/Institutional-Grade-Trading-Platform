from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict

class VerificationResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"

class CertificationMetrics(BaseModel):
    """Explicit performance metrics collected during certification."""
    sequential_duration_ms: float = 0.0
    parallel_duration_ms: float = 0.0
    incremental_duration_ms: float = 0.0
    reuse_percentage: float = 0.0
    peak_memory_mb: float = 0.0
    dataset_size: int = 0
    symbols_processed: int = 0

class CertificationReport(BaseModel):
    """The immutable permanent record of certification execution."""
    # Lineage
    phase_version: str = "7.6"
    pipeline_version: str = "1.0.0"
    config_hash: str
    business_fingerprint_version: int
    detection_algorithm_version: str
    quality_algorithm_version: str
    lifecycle_algorithm_version: str
    optimization_algorithm_version: str
    dataset_generator_version: str = "1.0.0"
    
    certification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    random_seed: int
    
    # Results
    stage_results: Dict[str, VerificationResult] = Field(default_factory=dict)
    metrics: CertificationMetrics = Field(default_factory=CertificationMetrics)
    
    # Status
    overall_status: VerificationResult = VerificationResult.SKIPPED
