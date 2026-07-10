from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
import hashlib
from pydantic import BaseModel, Field

class VerificationStageStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class VerificationResult(BaseModel):
    stage_name: str
    status: VerificationStageStatus
    duration_ms: float
    error_message: Optional[str] = None
    
    model_config = {"frozen": True}

class BenchmarkSummary(BaseModel):
    sequential_ms: float
    optimized_ms: float
    speedup_ratio: float
    cache_hit_rate: float
    reuse_percentage: float
    peak_memory_mb: float
    hardware_cpu: str
    python_version: str
    dataset_size: int
    number_of_candidates: int
    
    model_config = {"frozen": True}

class CoverageSummary(BaseModel):
    module_path: str
    percentage: float
    
    model_config = {"frozen": True}

class ConsolidationCertificationReport(BaseModel):
    certification_id: str
    pipeline_version: str
    configuration_version: int
    business_fingerprint_version: str
    detection_algorithm_version: str
    quality_algorithm_version: str
    lifecycle_algorithm_version: str
    optimization_algorithm_version: str
    
    verification_results: List[VerificationResult]
    benchmark_summary: Optional[BenchmarkSummary] = None
    coverage_summary: Optional[CoverageSummary] = None
    
    generated_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate_id(cls, timestamp: datetime) -> str:
        return hashlib.sha256(f"CERT_{timestamp.isoformat()}".encode("utf-8")).hexdigest()

    model_config = {"frozen": True}
