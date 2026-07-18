from typing import Any, Dict
from pydantic import BaseModel, Field

class BaseEvidence(BaseModel):
    """
    Base class for all evidence objects with provenance mapping.
    """
    snapshot_version: int = Field(description="The version of the upstream snapshot")
    dataset_version: int = Field(description="The dataset version used in the upstream snapshot")
    configuration_hash: str = Field(description="The configuration hash of the upstream engine")
    algorithm_version: str = Field(description="The algorithm version of the upstream engine")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata from the upstream engine")
    
    model_config = {"frozen": True}

class UniverseEvidence(BaseEvidence):
    """Evidence from the Universe Engine."""
    universe_state: str = Field(description="The state of the universe criteria")
    universe_score: float = Field(description="The computed score from the universe evaluation")

class WatchlistEvidence(BaseEvidence):
    """Evidence from the Watchlist Engine."""
    watchlist_state: str = Field(description="The state of the watchlist criteria")
    watchlist_score: float = Field(description="The computed score from the watchlist evaluation")

class TrendEvidence(BaseEvidence):
    """Evidence from the Trend Engine."""
    trend_state: str = Field(description="The primary trend state (e.g., UPTREND, DOWNTREND)")
    trend_quality: float = Field(description="The assessed quality of the trend")
    
class ConsolidationEvidence(BaseEvidence):
    """Evidence from the Consolidation Engine."""
    consolidation_state: str = Field(description="The primary consolidation state (e.g., RANGING, BREAKOUT)")
    consolidation_quality: float = Field(description="The assessed quality of the consolidation phase")

class LiquidityGrabEvidence(BaseEvidence):
    """Evidence from the Liquidity Grab Engine."""
    liquidity_grab_state: str = Field(description="The state of the liquidity grab")
    liquidity_grab_quality: float = Field(description="The quality of the liquidity grab")
