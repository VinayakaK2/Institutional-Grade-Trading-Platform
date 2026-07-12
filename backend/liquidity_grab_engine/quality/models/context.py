from pydantic import BaseModel, Field
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate
from backend.liquidity_grab_engine.detection.contracts.market_data import ICandleSeries
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration
from backend.liquidity_grab_engine.models.models import LiquidityGrabMetadata

class LiquidityGrabEvaluationContext(BaseModel):
    """
    Immutable execution context for the Liquidity Grab Quality Engine.
    Engine does not receive an entire Market Dataset.
    """
    candidate: LiquidityGrabCandidate = Field(description="The Liquidity Grab Candidate to evaluate")
    candle_series: ICandleSeries = Field(description="Strongly typed candle series")
    parent_trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    parent_consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    configuration: LiquidityGrabConfiguration = Field(description="Active configuration")
    metadata: LiquidityGrabMetadata = Field(description="Execution metadata")
    
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
