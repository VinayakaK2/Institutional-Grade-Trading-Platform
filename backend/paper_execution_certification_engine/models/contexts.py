from typing import Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from backend.paper_execution_certification_engine.config.config import CertificationConfig
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext

class PaperExecutionCertificationContext(BaseModel):
    """
    Isolates the input states and test vectors used by the certification engine.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    # Original optimization context to certify
    optimization_context: PaperExecutionOptimizationContext
    
    # Verification Dataset IDs and Fingerprints for reproducibility
    synthetic_dataset_a_id: str
    synthetic_dataset_a_hash: str
    synthetic_dataset_b_id: str
    synthetic_dataset_b_hash: str
    replay_dataset_id: str
    replay_dataset_hash: str
    stress_dataset_id: str
    stress_dataset_hash: str
    
    certification_configuration: CertificationConfig
    certification_metadata: Dict[str, Any] = Field(default_factory=dict)
