from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class CertificationStageResult(BaseModel):
    """
    Captures the result of a single certification verification stage.
    """
    stage_name: str
    status: str  # e.g., 'PASS', 'FAIL', 'COMPLETED'
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    
    model_config = {"frozen": True}

class CertificationReport(BaseModel):
    """
    Aggregates results from all certification stages.
    """
    stages: List[CertificationStageResult]
    
    model_config = {"frozen": True}
