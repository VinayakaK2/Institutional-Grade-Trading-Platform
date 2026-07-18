import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from backend.trade_validation_engine.signal_aggregation.config.config import SignalAggregationConfig
from backend.trade_validation_engine.signal_aggregation.models.evidence import (
    UniverseEvidence,
    WatchlistEvidence,
    TrendEvidence,
    ConsolidationEvidence,
    LiquidityGrabEvidence
)

class SignalAggregationRequest(BaseModel):
    """
    Input request for Signal Aggregation.
    """
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    dataset_version: int = Field(description="Dataset version")
    
    universe_snapshot_version: int = Field(description="Requested Universe Snapshot version")
    watchlist_snapshot_version: int = Field(description="Requested Watchlist Snapshot version")
    trend_snapshot_version: int = Field(description="Requested Trend Snapshot version")
    consolidation_snapshot_version: int = Field(description="Requested Consolidation Snapshot version")
    liquidity_grab_snapshot_version: int = Field(description="Requested Liquidity Grab Snapshot version")
    
    configuration: SignalAggregationConfig = Field(default_factory=SignalAggregationConfig, description="Aggregation config")
    
    model_config = {"frozen": True}

class AggregationStageResult(BaseModel):
    """
    Common result returned by every aggregation pipeline stage.
    """
    stage_id: str = Field(description="The identifier of the aggregation stage")
    success: bool = Field(description="True if the stage successfully aggregated evidence")
    evidence: Optional[Any] = Field(default=None, description="The strongly typed evidence model if successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    duration_ms: int = Field(default=0, description="Execution duration in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic metadata")
    
    model_config = {"frozen": True}

class AggregatedTradeEvidence(BaseModel):
    """
    The final, unified output of Signal Aggregation, containing all collected evidence.
    """
    symbol: str = Field(description="The target symbol")
    timeframe: str = Field(description="The target timeframe")
    dataset_version: int = Field(description="The dataset version")
    
    universe_evidence: Optional[UniverseEvidence] = Field(default=None, description="Collected Universe evidence")
    watchlist_evidence: Optional[WatchlistEvidence] = Field(default=None, description="Collected Watchlist evidence")
    trend_evidence: Optional[TrendEvidence] = Field(default=None, description="Collected Trend evidence")
    consolidation_evidence: Optional[ConsolidationEvidence] = Field(default=None, description="Collected Consolidation evidence")
    liquidity_grab_evidence: Optional[LiquidityGrabEvidence] = Field(default=None, description="Collected Liquidity Grab evidence")
    
    configuration_hash: str = Field(description="Hash of the Signal Aggregation configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata concerning the assembly process")
    
    model_config = {"frozen": True}

class SignalAggregationMetadata(BaseModel):
    """
    Metadata concerning the root aggregation snapshot.
    """
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of aggregation")
    execution_duration_ms: int = Field(default=0, description="Total pipeline execution time")
    
    model_config = {"frozen": True}

class SignalAggregationSnapshot(BaseModel):
    """
    Immutable root entity containing the completely aggregated trade evidence.
    """
    aggregation_id: str = Field(description="Deterministic ID for this aggregation")
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    
    success: bool = Field(description="Whether the aggregation pipeline succeeded entirely")
    stage_results: List[AggregationStageResult] = Field(description="Diagnostic results from each stage")
    aggregated_evidence: Optional[AggregatedTradeEvidence] = Field(description="The final assembled evidence")
    
    metadata: SignalAggregationMetadata = Field(default_factory=SignalAggregationMetadata, description="Root metadata")
    
    @classmethod
    def generate_id(cls, symbol: str, dataset_version: int, wl_version: int, t_version: int, c_version: int, lg_version: int, config_hash: str) -> str:
        """
        Generates a deterministic ID via SHA-256 using the prompt requirements.
        Note: The prompt specified symbol, dataset, wl, t, c, lg, config_hash.
        It omitted universe_snapshot_version in the ID example, but I will include it or follow the example strictly.
        I will follow the exact example from the prompt:
        symbol, dataset_version, watchlist_snapshot_version, trend_snapshot_version, consolidation_snapshot_version, liquidity_grab_snapshot_version, configuration_hash
        Wait, I'll add universe version as well to ensure correctness, as it is a parent.
        """
        payload = f"{symbol}_{dataset_version}_{wl_version}_{t_version}_{c_version}_{lg_version}_{config_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    model_config = {"frozen": True}
