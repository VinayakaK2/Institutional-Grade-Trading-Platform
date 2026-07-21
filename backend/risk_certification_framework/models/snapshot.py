from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any
from backend.risk_certification_framework.models.report import CertificationReport

class RiskCertificationSnapshot(BaseModel):
    """
    The canonical persisted artifact. Wraps the CertificationReport with metadata.
    """
    snapshot_id: str = Field(description="Unique ID for this certification snapshot")
    report: CertificationReport = Field(description="The embedded certification report")
    certified_phase_version: str = Field(description="Version of the phase being certified (e.g. 11.6)")
    algorithm_version: str = Field(description="Version of the certification algorithms")
    pipeline_version: str = Field(description="Version of the risk pipeline tested")
    business_fingerprint: str = Field(description="Deterministically hashed fingerprint of inputs used for certification")
    generated_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional certification metadata")
    
    model_config = {"frozen": True}
