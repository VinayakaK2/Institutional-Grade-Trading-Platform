import json
import hashlib
from typing import List
from pydantic import BaseModel, Field

class ConsolidationLifecycleConfiguration(BaseModel):
    """Configuration for Consolidation Lifecycle Engine."""
    config_version: int = Field(default=1, description="Version of this configuration")
    
    # State precedence (Index 0 is highest precedence, then 1, etc.)
    # Based on user requirements: ENDED > BROKEN > WEAKENING > CONTINUING > ACTIVE
    state_precedence: List[str] = Field(
        default=["ENDED", "BROKEN", "WEAKENING", "CONTINUING", "ACTIVE"],
        description="Deterministic precedence of states if multiple evidence types trigger."
    )
    
    def compute_hash(self) -> str:
        data = self.model_dump(mode="json")
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
        
    model_config = {"frozen": True}
