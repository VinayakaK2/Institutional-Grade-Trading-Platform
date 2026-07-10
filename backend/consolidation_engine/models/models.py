import hashlib
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from backend.consolidation_engine.config.config import ConsolidationConfiguration

class ConsolidationCandidate(BaseModel):
    candidate_id: str = Field(description="Deterministic ID based on symbol, timeframe, start, end, and fingerprint.")
    symbol: str = Field(description="Symbol string (e.g. AAPL:NASDAQ)")
    timeframe: str = Field(description="Timeframe string (e.g. 1d, 1h)")
    start_timestamp: datetime = Field(description="Start time of the consolidation")
    end_timestamp: datetime = Field(description="End time of the consolidation")
    upper_boundary: float = Field(description="Upper boundary price")
    lower_boundary: float = Field(description="Lower boundary price")
    midpoint: float = Field(description="Midpoint price")
    duration: int = Field(description="Duration in seconds")
    candle_count: int = Field(description="Number of candles in consolidation")
    
    @classmethod
    def generate_id(cls, symbol: str, timeframe: str, start_timestamp: datetime, end_timestamp: datetime, business_fingerprint: str) -> str:
        payload = f"{symbol}_{timeframe}_{start_timestamp.timestamp()}_{end_timestamp.timestamp()}_{business_fingerprint}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
    model_config = {"frozen": True}

class ConsolidationSnapshot(BaseModel):
    snapshot_version: int = Field(description="Version of this snapshot")
    parent_dataset_version: int = Field(description="Version of the parent market dataset")
    parent_trend_snapshot_version: int = Field(..., description="Version of the Trend Snapshot this was generated from")
    pipeline_version: str = Field(..., description="Overall pipeline version (e.g. 1.0)")
    engine_version: str = Field(default="1.0", description="Version of the Consolidation Engine")
    config_version: int = Field(..., description="Configuration version used")
    config_hash: str = Field(description="Configuration hash")
    business_fingerprint: str = Field(description="Deterministic business fingerprint hash")
    fingerprint_algorithm_version: int = Field(description="Version of the fingerprint algorithm")
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    candidates: List[ConsolidationCandidate] = Field(default_factory=list, description="List of detected consolidations")
    
    model_config = {"frozen": True}

class ConsolidationMetadata(BaseModel):
    """Metadata regarding the execution of the Consolidation Pipeline."""
    execution_start_timestamp: datetime = Field(description="When pipeline execution began")
    execution_end_timestamp: Optional[datetime] = Field(default=None, description="When pipeline execution ended")
    total_candidates_detected: int = Field(default=0, description="Total number of candidates detected")
    pipeline_version: str = Field(..., description="Version of the pipeline executed")
    
    model_config = {"frozen": True}

class ConsolidationExecutionContext(BaseModel):
    """Immutable context carried through the pipeline. Does not contain mutable state."""
    # Assuming MarketDataset and TrendSnapshot are defined elsewhere, we pass their identifiers/versions or objects if needed.
    # For Phase 8.1 we only need the structure.
    dataset_version: int = Field(..., description="Market dataset version")
    trend_snapshot_version: int = Field(..., description="Trend snapshot version used as input")
    configuration: "ConsolidationConfiguration" = Field(..., description="The configuration for this run")
    metadata: ConsolidationMetadata = Field(..., description="Execution metadata")
    
    model_config = {"frozen": True}
