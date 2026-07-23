from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class StageResult(BaseModel):
    """Result of a single certification pipeline stage."""
    model_config = ConfigDict(frozen=True)
    
    stage_name: str
    passed: bool
    evidence: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    duration_ms: float

class CertificationMetadata(BaseModel):
    """Metadata for the certification snapshot."""
    model_config = ConfigDict(frozen=True)
    
    certified_at: datetime
    execution_duration_ms: float

class CertificationReport(BaseModel):
    """Rich summary report generated at the end of the pipeline."""
    model_config = ConfigDict(frozen=True)
    
    certification_id: str
    certification_schema_version: str
    certified: bool
    paper_execution_version: str
    optimization_version: str
    certification_version: str
    timestamp: str
    business_fingerprint: str
    canonical_hash: str
    evidence_count: int
    verified_stages: List[StageResult]

class PaperExecutionCertificationSnapshot(BaseModel):
    """Immutable certification snapshot."""
    model_config = ConfigDict(frozen=True)
    
    snapshot_version: str
    certification_id: str
    certification_version: str
    certification_report: CertificationReport
    business_fingerprint: str
    canonical_hash: str
    parent_execution_snapshot_version: str
    certification_metadata: CertificationMetadata
