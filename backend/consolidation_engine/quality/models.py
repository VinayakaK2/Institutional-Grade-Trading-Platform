import hashlib
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List

from backend.consolidation_engine.models.models import ConsolidationCandidate
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.quality.config import ConsolidationQualityConfiguration

class ConsolidationQualityLevel(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"
    REJECTED = "REJECTED"

class ConsolidationQualityMetrics(BaseModel):
    range_stability: float = Field(description="Score (0-1) for range stability")
    boundary_respect: float = Field(description="Score (0-1) for boundary respect")
    price_containment: float = Field(description="Score (0-1) for price containment")
    candle_consistency: float = Field(description="Score (0-1) for candle consistency")
    consolidation_duration: int = Field(description="Score/Count representing duration")
    range_symmetry: float = Field(description="Score (0-1) for range symmetry")
    
    model_config = {"frozen": True}

class ConsolidationEvaluationContext(BaseModel):
    """Immutable context carried through the Quality Engine."""
    candidate: ConsolidationCandidate
    candles: List[Candle] = Field(..., description="Candles belonging only to the candidate")
    dataset_version: int = Field(description="Version of the parent market dataset")
    symbol: str
    timeframe: str
    configuration: ConsolidationQualityConfiguration
    
    model_config = {"frozen": True}

class ConsolidationQualityReport(BaseModel):
    report_id: str = Field(description="Deterministic report ID")
    candidate_id: str = Field(description="ID of the candidate evaluated")
    symbol: str
    timeframe: str
    metrics: ConsolidationQualityMetrics
    quality_level: ConsolidationQualityLevel
    config_version: int
    algorithm_version: str
    generated_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate_id(cls, candidate_id: str, config_hash: str, algorithm_version: str) -> str:
        payload = f"{candidate_id}_{config_hash}_{algorithm_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
    model_config = {"frozen": True}
