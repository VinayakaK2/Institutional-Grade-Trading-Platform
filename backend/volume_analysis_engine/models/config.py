from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class AverageVolumeType(str, Enum):
    SMA = "sma"
    EMA = "ema"

class VolumeAnalysisConfig(BaseModel):
    """
    Configuration for Volume Analysis.
    """
    model_config = ConfigDict(frozen=True)
    
    avg_volume_type: AverageVolumeType = AverageVolumeType.SMA
    avg_volume_period: int = Field(default=20, gt=0)
    
    # Validation threshold
    minimum_history_required: int = Field(default=20, gt=0)
    
    # Event thresholds (multipliers of average volume)
    expansion_threshold: float = Field(default=1.5, gt=1.0)
    contraction_threshold: float = Field(default=0.7, gt=0.0, lt=1.0)
    climax_threshold: float = Field(default=3.0, gt=1.0)
    dry_volume_threshold: float = Field(default=0.3, gt=0.0, lt=1.0)
