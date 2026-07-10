from pydantic import BaseModel, Field

class TrendLifecycleConfig(BaseModel):
    """
    Configuration for Phase 7.4: Trend Lifecycle Engine.
    Controls the thresholds for detecting weakening, breaks, and lifecycle endings.
    """
    
    # ---------------------------------------------------------
    # Versioning
    # ---------------------------------------------------------
    lifecycle_rule_version: int = Field(
        default=1,
        description="Version tracking business threshold and parameter changes."
    )
    
    lifecycle_algorithm_version: str = Field(
        default="1.0.0",
        description="Version string identifying the exact logic implementation used."
    )

    # ---------------------------------------------------------
    # Weakening Thresholds
    # ---------------------------------------------------------
    min_quality_drop_percent: float = Field(
        default=20.0,
        description="Minimum percentage drop in quality score to flag a trend as weakening."
    )
    
    weakening_ema_separation_ratio_threshold: float = Field(
        default=0.5,
        description="If EMA separation drops below this ratio (%), flag as weakening."
    )

    # ---------------------------------------------------------
    # Break Thresholds
    # ---------------------------------------------------------
    max_structural_noise_percent: float = Field(
        default=50.0,
        description="Maximum structural noise allowed before marking trend as BROKEN."
    )

    # ---------------------------------------------------------
    # End Thresholds
    # ---------------------------------------------------------
    min_neutral_bars_to_end: int = Field(
        default=3,
        description="Number of consecutive neutral bars before marking an active trend as ENDED."
    )
    
    min_quality_score_to_maintain: float = Field(
        default=0.1,
        description="If normalized quality drops below this absolute threshold, flag as ENDED."
    )
