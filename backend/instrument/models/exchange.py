"""
Exchange Models
"""
from pydantic import BaseModel, Field

class ExchangeMetadata(BaseModel):
    """
    Reusable exchange abstraction for the platform.
    """
    code: str = Field(..., description="Internal normalized exchange code (e.g., NSE, NASDAQ, NYSE)")
    name: str = Field(..., description="Full name of the exchange")
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code (e.g., IN, US)")
    timezone: str = Field(..., description="IANA timezone name (e.g., Asia/Kolkata, America/New_York)")
    is_active: bool = Field(default=True, description="Whether the exchange is currently active/supported")
