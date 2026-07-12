import hashlib
from typing import List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration

class LiquidityGrabPipelineVersion(BaseModel):
    version: str = Field(description="Pipeline version string")
    model_config = {"frozen": True}

class LiquidityGrabConfigurationReference(BaseModel):
    version: int = Field(description="Configuration version")
    config_hash: str = Field(description="Hash of the configuration")
    model_config = {"frozen": True}

class LiquidityGrabMetadata(BaseModel):
    execution_start_timestamp: datetime = Field(description="Pipeline execution start time")
    execution_end_timestamp: Optional[datetime] = Field(default=None, description="Pipeline execution end time")
    pipeline_version: str = Field(description="Version of the pipeline executed")
    model_config = {"frozen": True}

class LiquidityGrabExecutionContext(BaseModel):
    symbol: SymbolReference = Field(description="Target symbol")
    timeframe: Timeframe = Field(description="Target timeframe")
    dataset_version: int = Field(description="Explicit dataset version")
    parent_trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    parent_consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    configuration: LiquidityGrabConfiguration = Field(description="Active configuration")
    metadata: LiquidityGrabMetadata = Field(description="Execution metadata")
    model_config = {"frozen": True}

class LiquidityGrabSnapshot(BaseModel):
    snapshot_id: str = Field(description="Deterministic ID for this snapshot")
    symbol_id: str = Field(description="Target symbol ID")
    timeframe: str = Field(description="Target timeframe")
    snapshot_version: int = Field(description="Version of this snapshot")
    dataset_version: int = Field(description="Dataset version used")
    parent_trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    parent_consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    
    pipeline_version: str = Field(description="Pipeline version used")
    config_reference: LiquidityGrabConfigurationReference = Field(description="Configuration reference")
    
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    # Placeholder for future Phase 9.2+ data
    grabs: List[Any] = Field(default_factory=list, description="List of detected liquidity grabs (structural only for 9.1)")
    
    @classmethod
    def generate_id(cls, symbol_id: str, timeframe: str, dataset_version: int, trend_version: int, consolidation_version: int) -> str:
        payload = f"{symbol_id}_{timeframe}_{dataset_version}_{trend_version}_{consolidation_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
    model_config = {"frozen": True}
