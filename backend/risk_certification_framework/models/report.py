from pydantic import BaseModel, Field
from backend.risk_certification_framework.models.record import VerificationRecord

class CertificationReport(BaseModel):
    """
    Structured verification record for all certification checks.
    """
    overall_status: str = Field(description="Overall certification status (PASS/FAIL)")
    functional_record: VerificationRecord = Field(description="Result of functional verification")
    determinism_record: VerificationRecord = Field(description="Result of determinism verification")
    repository_record: VerificationRecord = Field(description="Result of repository verification")
    stress_record: VerificationRecord = Field(description="Result of stress verification")
    performance_record: VerificationRecord = Field(description="Result of performance verification")
    regression_record: VerificationRecord = Field(description="Result of regression verification")
    
    model_config = {"frozen": True}
