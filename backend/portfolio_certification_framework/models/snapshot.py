from pydantic import BaseModel
from backend.shared.snapshots.models import BaseSnapshot
from backend.portfolio_certification_framework.models.certification_models import CertificationReport

class PortfolioCertificationMetadata(BaseModel):
    """
    Metadata about the certification execution environment.
    """
    engine_version: str
    pipeline_version: str
    
    model_config = {"frozen": True}

class PortfolioCertificationSnapshot(BaseSnapshot):
    """
    The final, immutable, canonical payload created by the Certification Engine.
    """
    portfolio_optimization_snapshot_id: str
    configuration_snapshot_id: str
    dataset_version: str
    business_fingerprint: str
    
    certification_report: CertificationReport
    certification_metadata: PortfolioCertificationMetadata
    
    model_config = {"frozen": True}
