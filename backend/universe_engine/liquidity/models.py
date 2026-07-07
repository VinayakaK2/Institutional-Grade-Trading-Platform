from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from backend.universe_engine.models.universe import UniverseInstrument

class LiquidityFilterConfiguration(BaseModel):
    """Configuration for liquidity filters."""
    volume_lookback_days: int = Field(default=30, description="Lookback period for ADV calculation.")
    min_average_daily_volume: int = Field(default=500000, description="Minimum ADV threshold.")
    
    turnover_lookback_days: int = Field(default=30, description="Lookback period for ADT calculation.")
    min_average_daily_turnover: float = Field(default=1000000.0, description="Minimum ADT threshold.")
    
    price_lookback_days: int = Field(default=1, description="Lookback period for price evaluation.")
    min_close_price: float = Field(default=5.0, description="Minimum close price threshold (prevents penny stocks).")
    
    min_market_capitalization: float = Field(default=50000000.0, description="Minimum market cap threshold.")


class LiquidityRejectionReason(str, Enum):
    """Reasons why an instrument failed liquidity qualification."""
    VOLUME_BELOW_THRESHOLD = "VOLUME_BELOW_THRESHOLD"
    TURNOVER_BELOW_THRESHOLD = "TURNOVER_BELOW_THRESHOLD"
    PRICE_BELOW_THRESHOLD = "PRICE_BELOW_THRESHOLD"
    MARKET_CAP_BELOW_THRESHOLD = "MARKET_CAP_BELOW_THRESHOLD"
    MISSING_DATA = "MISSING_DATA"


class RejectionDetail(BaseModel):
    """Structured details of why an instrument was rejected."""
    instrument_symbol: str
    stage_name: str
    reason: LiquidityRejectionReason
    measured_value: Optional[str]
    threshold: str


class LiquidityFilterStatistics(BaseModel):
    """Operational metrics and rejection counts for a filter run."""
    initial_instrument_count: int = 0
    final_qualified_count: int = 0
    volume_rejections: int = 0
    turnover_rejections: int = 0
    price_rejections: int = 0
    market_cap_rejections: int = 0
    missing_data_rejections: int = 0
    processing_time_ms: float = 0.0
    pipeline_version: str = "1.0.0"


class LiquidityFilterContext(BaseModel):
    """State maintained during a liquidity filter pipeline execution."""
    run_id: str
    parent_snapshot_id: str
    config: LiquidityFilterConfiguration
    
    qualified_instruments: List[UniverseInstrument]
    rejected_details: List[RejectionDetail] = Field(default_factory=list)
    statistics: LiquidityFilterStatistics = Field(default_factory=LiquidityFilterStatistics)
    liquidity_metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Execution metadata
    started_at: datetime


class LiquidityQualifiedUniverse(BaseModel):
    """
    Immutable resulting artifact of the Liquidity Filter Engine.
    Must never be mutated after generation.
    """
    liquidity_universe_id: str = Field(description="Unique ID for this qualified universe")
    parent_snapshot_id: str = Field(description="ID of the structural universe snapshot it was based on")
    pipeline_version: str = Field(description="Pipeline version during execution")
    config_hash: str = Field(description="Hash of the configuration used")
    created_at: datetime = Field(description="When this universe was generated")
    
    qualified_symbols: List[UniverseInstrument]
    rejected_symbols: List[RejectionDetail]
    configuration_snapshot: LiquidityFilterConfiguration
    statistics: LiquidityFilterStatistics
    liquidity_metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    class Config:
        frozen = True


class LiquidityFilterResult(BaseModel):
    """Result returned by the LiquidityFilterEngine to the caller."""
    universe: LiquidityQualifiedUniverse
