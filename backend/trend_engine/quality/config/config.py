"""
Trend Quality Engine Configuration
==================================

Strongly typed configuration for the Trend Quality Engine.
Defines thresholds for strength, pullback depth, and persistence logic.
"""

from pydantic import BaseModel, ConfigDict, Field


class TrendQualityConfig(BaseModel):
    """
    Configuration parameters for Trend Quality evaluation.
    
    All thresholds defined here dictate how raw mathematical outputs 
    are processed or bounded before normalization.
    """
    model_config = ConfigDict(frozen=True)

    # ---------------------------------------------------------
    # Versioning
    # ---------------------------------------------------------
    configuration_version: int = Field(
        default=1,
        description="Human-readable version of this configuration schema and its thresholds."
    )
    quality_algorithm_version: str = Field(
        default="1.0.0",
        description="Version string identifying the exact mathematical aggregation algorithm used."
    )

    # ---------------------------------------------------------
    # Strength Evaluation Thresholds
    # ---------------------------------------------------------
    min_ema_separation_ratio: float = Field(
        default=0.005,  # 0.5%
        description="Minimum ratio of separation between fast/medium/slow EMAs to be considered strong."
    )
    max_ema_separation_ratio: float = Field(
        default=0.05,  # 5%
        description="Maximum expected separation. Beyond this is considered exceptionally strong/extended."
    )

    # ---------------------------------------------------------
    # Pullback Evaluation Thresholds
    # ---------------------------------------------------------
    max_pullback_depth_percent: float = Field(
        default=0.10,  # 10%
        description="Maximum depth of a pullback against the trend before it might be considered a breakdown."
    )
    max_pullback_duration_bars: int = Field(
        default=10,
        description="Maximum number of bars a pullback can last before the trend quality degrades."
    )

    # ---------------------------------------------------------
    # Consistency Evaluation Thresholds
    # ---------------------------------------------------------
    min_structure_points_required: int = Field(
        default=3,
        description="Minimum number of HH/HL or LH/LL points required to evaluate sequence consistency."
    )

    # ---------------------------------------------------------
    # Persistence Evaluation Thresholds
    # ---------------------------------------------------------
    min_trend_age_bars: int = Field(
        default=5,
        description="Minimum number of bars the trend must have existed to be evaluated."
    )
    mature_trend_age_bars: int = Field(
        default=20,
        description="Number of bars at which a trend is considered fully mature for normalization purposes."
    )
