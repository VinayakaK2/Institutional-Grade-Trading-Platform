"""
Trend Quality Domain Models
===========================

Immutable domain models representing the quality of a previously detected trend.
These models strictly describe mathematical properties of the trend and DO NOT 
generate buy/sell signals or risk probabilities.
"""

from pydantic import BaseModel, ConfigDict
from typing import List


class TrendStrengthResult(BaseModel):
    """Real mathematical measurements of trend strength."""
    model_config = ConfigDict(frozen=True)

    ema_separation_ratio: float
    direction_stability_percent: float
    is_extended: bool


class TrendConsistencyResult(BaseModel):
    """Real mathematical measurements of structural sequence consistency."""
    model_config = ConfigDict(frozen=True)

    sequence_stability_ratio: float
    structural_noise_percent: float
    valid_structures_count: int


class PullbackQualityResult(BaseModel):
    """Real mathematical measurements of pullback behavior during the trend."""
    model_config = ConfigDict(frozen=True)

    average_pullback_depth_percent: float
    average_pullback_duration_bars: float
    pullback_count: int
    deepest_pullback_percent: float


class TrendPersistenceResult(BaseModel):
    """Real measurements of the trend's persistence over time."""
    model_config = ConfigDict(frozen=True)

    trend_age_bars: int
    interruption_count: int
    longest_uninterrupted_run_bars: int


class NormalizedQualityMetrics(BaseModel):
    """
    Unit-less, normalized (e.g. 0.0 to 1.0) representations of the raw quality outputs.
    Allows for deterministic aggregation without changing the underlying mathematical meaning.
    """
    model_config = ConfigDict(frozen=True)

    normalized_strength: float
    normalized_consistency: float
    normalized_pullback_quality: float
    normalized_persistence: float


class TrendQualitySymbolResult(BaseModel):
    """
    Immutable root entity encapsulating all quality metrics evaluated for a single trend symbol.
    """
    model_config = ConfigDict(frozen=True)

    # Identifies the symbol in the parent snapshot
    symbol_key: str
    
    # Descriptive metrics
    strength_metrics: TrendStrengthResult
    consistency_metrics: TrendConsistencyResult
    pullback_metrics: PullbackQualityResult
    persistence_metrics: TrendPersistenceResult
    
    # Normalized equivalents
    normalized_metrics: NormalizedQualityMetrics


class TrendQualityMetadata(BaseModel):
    """
    Descriptive audit metadata about the generation of a Trend Quality Snapshot.
    """
    model_config = ConfigDict(frozen=True)

    pipeline_version: str
    configuration_hash: str
    configuration_version: int
    quality_algorithm_version: str
    evaluation_timestamp: str
    evaluation_duration_ms: float


class TrendQualitySnapshot(BaseModel):
    """
    Immutable root entity encapsulating all quality evaluations for an entire TrendSnapshot.
    """
    model_config = ConfigDict(frozen=True)

    # Unique identity for this quality evaluation run
    quality_snapshot_id: str
    
    # Lineage pointer to the parent detection snapshot
    source_trend_snapshot_id: str
    
    # Quality evaluations for each symbol in the parent snapshot
    symbols: List[TrendQualitySymbolResult]
    
    metadata: TrendQualityMetadata
