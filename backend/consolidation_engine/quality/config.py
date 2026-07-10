import hashlib
import json
from pydantic import BaseModel, Field

class ConsolidationQualityConfiguration(BaseModel):
    """Configuration for Consolidation Quality Evaluation."""
    config_version: int = Field(default=1, description="Version of this configuration")
    
    # Weights for metrics to calculate a final score
    weight_range_stability: float = Field(default=0.2)
    weight_boundary_respect: float = Field(default=0.2)
    weight_price_containment: float = Field(default=0.2)
    weight_candle_consistency: float = Field(default=0.2)
    weight_range_symmetry: float = Field(default=0.2)
    
    # Duration doesn't strictly have a 0-1 bound natively unless normalized.
    ideal_duration_candles: int = Field(default=20)
    weight_duration: float = Field(default=0.0)
    
    # Thresholds for classification
    excellent_threshold: float = Field(default=0.85)
    good_threshold: float = Field(default=0.70)
    acceptable_threshold: float = Field(default=0.50)
    poor_threshold: float = Field(default=0.30)
    
    def compute_hash(self) -> str:
        data = self.model_dump(mode="json")
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
        
    model_config = {"frozen": True}
