"""
Freshness Engine Configuration
==============================

Configuration specific to the Freshness & Availability Engine.
"""
from pydantic import BaseModel, Field

class FreshnessSettings(BaseModel):
    """
    Settings for the Freshness Engine.
    """
    # Maximum allowed age for the latest candle in calendar days.
    # If the latest candle is older than this, the symbol is rejected.
    max_data_age_days: int = Field(default=3, description="Maximum allowed age of the latest candle in days.")
    
    # Expected number of recent candles to examine for structural integrity
    # (e.g. checking for duplicates, strictly monotonic timestamps).
    integrity_check_lookback: int = Field(default=5, description="Number of recent candles to check for integrity.")
