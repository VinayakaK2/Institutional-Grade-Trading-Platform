from typing import List
from backend.core.config import AppSettings
from pydantic import Field

class MarketBuilderConfig(AppSettings):
    """
    Configuration for the Market Universe Builder.
    Defines the filtering rules for exchange selection, market segments,
    instrument types, and trading status.
    """
    allowed_exchanges: List[str] = Field(
        default_factory=lambda: ["NSE", "BSE"],
        description="List of allowed exchange codes."
    )
    
    allowed_market_segments: List[str] = Field(
        default_factory=lambda: ["EQUITY_CASH"],
        description="List of allowed market segment names."
    )
    
    allowed_instrument_types: List[str] = Field(
        default_factory=lambda: ["EQUITY", "ETF"],
        description="List of allowed instrument type names."
    )
    
    rejected_trading_statuses: List[str] = Field(
        default_factory=lambda: ["SUSPENDED", "HALTED", "DISABLED", "INACTIVE", "UNKNOWN"],
        description="List of trading statuses that will cause an instrument to be rejected."
    )
    
    remove_delisted: bool = Field(
        default=True,
        description="If True, instruments marked as delisted are removed."
    )
