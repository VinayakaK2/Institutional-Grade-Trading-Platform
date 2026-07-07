from datetime import datetime
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field, ConfigDict

from backend.universe_engine.models.universe import UniverseInstrument

class MarketCapClassification(str, Enum):
    LARGE = "LARGE"
    MID = "MID"
    SMALL = "SMALL"
    UNKNOWN = "UNKNOWN"

class LiquidityClassification(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

class DataQualityClassification(str, Enum):
    CERTIFIED = "CERTIFIED"

class ClassifiedSymbol(BaseModel):
    """
    Combines the structural instrument with its classifications.
    """
    symbol: UniverseInstrument
    sector: str = "UNKNOWN"
    industry: str = "UNKNOWN"
    market_cap: MarketCapClassification = MarketCapClassification.UNKNOWN
    liquidity: LiquidityClassification = LiquidityClassification.UNKNOWN
    data_quality: DataQualityClassification = DataQualityClassification.CERTIFIED

class UniverseClassificationConfiguration(BaseModel):
    """
    Thresholds and configurations for classification categories.
    """
    large_cap_threshold: float = Field(default=10_000_000_000.0, description="Minimum market cap for Large Cap.")
    mid_cap_threshold: float = Field(default=2_000_000_000.0, description="Minimum market cap for Mid Cap.")
    
    high_liquidity_volume_threshold: float = Field(default=5_000_000.0, description="Minimum ADV for High Liquidity.")
    medium_liquidity_volume_threshold: float = Field(default=1_000_000.0, description="Minimum ADV for Medium Liquidity.")


class UniverseClassificationStatistics(BaseModel):
    """
    Immutable statistics for a classification run.
    """
    total_symbols: int = 0
    sector_distribution: Dict[str, int] = Field(default_factory=dict)
    industry_distribution: Dict[str, int] = Field(default_factory=dict)
    market_cap_distribution: Dict[str, int] = Field(default_factory=dict)
    liquidity_distribution: Dict[str, int] = Field(default_factory=dict)
    data_quality_distribution: Dict[str, int] = Field(default_factory=dict)
    
    unknown_sector_count: int = 0
    unknown_industry_count: int = 0
    
    processing_time_ms: float = 0.0
    pipeline_version: str = "1.0.0"


class UniverseClassificationContext(BaseModel):
    """
    Mutable state passed through classification stages.
    """
    run_id: str
    parent_certified_universe_id: str
    config: UniverseClassificationConfiguration
    
    # Starting with base instruments, stages modify these classified symbols.
    classified_symbols: Dict[str, ClassifiedSymbol] = Field(default_factory=dict)
    
    # We pass the parent's liquidity metrics here to avoid loading them repeatedly.
    parent_liquidity_metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    statistics: UniverseClassificationStatistics = Field(default_factory=UniverseClassificationStatistics)
    started_at: datetime


class ClassifiedUniverse(BaseModel):
    """
    Immutable resulting artifact of the Classification Engine.

    CLASSIFICATION STABILITY:
    ─────────────────────────
    ClassifiedUniverse snapshots are strictly immutable. If provider metadata 
    (e.g., sector, industry, market cap) changes, a NEW ClassifiedUniverse snapshot 
    must be generated and persisted. Existing snapshots are NEVER modified or 
    backfilled to reflect new metadata. This preserves absolute auditability.
    """
    model_config = ConfigDict(frozen=True)

    classified_universe_id: str = Field(description="Unique ID for this classified universe")
    parent_certified_universe_id: str = Field(description="ID of the certified universe snapshot it was based on")
    pipeline_version: str = Field(description="Pipeline version during execution")
    config_hash: str = Field(description="Hash of the configuration used")
    created_at: datetime = Field(description="When this universe was classified")
    
    classified_symbols: List[ClassifiedSymbol]
    configuration_snapshot: UniverseClassificationConfiguration
    statistics: UniverseClassificationStatistics


class UniverseClassificationResult(BaseModel):
    """Result returned by the UniverseClassificationEngine to the caller."""
    universe: ClassifiedUniverse
