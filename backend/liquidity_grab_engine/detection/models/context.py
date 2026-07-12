from pydantic import BaseModel, Field
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration
from backend.liquidity_grab_engine.models.models import LiquidityGrabMetadata
from backend.liquidity_grab_engine.detection.contracts.market_data import ICandleSeries

class DatasetContext(BaseModel):
    version: int = Field(description="Explicit dataset version")
    model_config = {"frozen": True}

class ParentSnapshotsContext(BaseModel):
    trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    model_config = {"frozen": True}

class MarketDataContext(BaseModel):
    symbol: SymbolReference = Field(description="Target symbol")
    timeframe: Timeframe = Field(description="Target timeframe")
    candle_series: ICandleSeries = Field(description="Strongly typed candle series abstraction")
    model_config = {"frozen": True, "arbitrary_types_allowed": True}

class LiquidityGrabDetectionContext(BaseModel):
    """
    Execution context for the Liquidity Grab Detection Engine.
    Organized into logical immutable sections.
    """
    dataset: DatasetContext = Field(description="Dataset information")
    parent_snapshots: ParentSnapshotsContext = Field(description="Parent snapshot references")
    market_data: MarketDataContext = Field(description="Market data inputs")
    configuration: LiquidityGrabConfiguration = Field(description="Active configuration")
    metadata: LiquidityGrabMetadata = Field(description="Execution metadata")
    
    model_config = {"frozen": True}
