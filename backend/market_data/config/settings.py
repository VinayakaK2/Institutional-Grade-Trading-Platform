"""
Market Data Provider Configuration
"""
from typing import List
from pydantic import Field
from backend.infrastructure.config.settings import AppSettings

class MarketDataSettings(AppSettings):
    """Market Data specific configurations."""
    
    # Ordered list of provider identifiers for automatic failover (e.g., ["zerodha", "binance", "yahoo"])
    primary_provider: str = Field(default="mock_provider", description="Primary data source")
    failover_providers: List[str] = Field(default_factory=list, description="Fallback sources if primary fails")
    
    # Global Limits
    max_retries_per_provider: int = Field(default=3, description="Max retries before failing over")
    provider_timeout_seconds: float = Field(default=5.0, description="Global timeout for provider HTTP calls")

market_data_settings = MarketDataSettings()
