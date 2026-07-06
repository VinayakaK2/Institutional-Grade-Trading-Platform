from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    """
    Represents a single finding during validation.
    """
    rule_name: str
    is_valid: bool
    record_timestamp: Optional[str] = None
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class ValidationCategoryFindings(BaseModel):
    errors: List[ValidationResult] = Field(default_factory=list)
    warnings: List[ValidationResult] = Field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

class ValidationReport(BaseModel):
    """
    Structured Validation Report.
    """
    # Summary
    total_records_processed: int = 0
    valid_records_count: int = 0
    invalid_records_count: int = 0
    
    # Findings
    structural_findings: ValidationCategoryFindings = Field(default_factory=ValidationCategoryFindings)
    ohlcv_findings: ValidationCategoryFindings = Field(default_factory=ValidationCategoryFindings)
    gap_findings: ValidationCategoryFindings = Field(default_factory=ValidationCategoryFindings)
    anomaly_findings: ValidationCategoryFindings = Field(default_factory=ValidationCategoryFindings)
    
    # Execution Metadata
    duration_seconds: float = 0.0
    execution_time: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def is_completely_valid(self) -> bool:
        return (
            self.structural_findings.is_valid and
            self.ohlcv_findings.is_valid and
            self.gap_findings.is_valid and
            self.anomaly_findings.is_valid
        )
