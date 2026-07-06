from enum import Enum

class AdjustmentMode(str, Enum):
    """Configurable modes for corporate action adjustments."""
    RAW = "RAW"
    FULLY_ADJUSTED = "FULLY_ADJUSTED"
    PRICE_ADJUSTED_ONLY = "PRICE_ADJUSTED_ONLY"
    VOLUME_ADJUSTED_ONLY = "VOLUME_ADJUSTED_ONLY"
