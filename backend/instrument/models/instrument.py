"""
Instrument Models
"""
from enum import Enum
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class InstrumentType(str, Enum):
    """Supported instrument types."""
    EQUITY = "EQUITY"
    ETF = "ETF"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"

class InstrumentStatus(str, Enum):
    """Trading status of an instrument."""
    ACTIVE = "ACTIVE"
    DELISTED = "DELISTED"
    SUSPENDED = "SUSPENDED"

class InstrumentIdentity(BaseModel):
    """
    Core identity of an instrument. 
    Designed for future identifier extensibility without breaking public APIs.
    """
    symbol: str = Field(..., description="Local exchange symbol (e.g., AAPL, RELIANCE)")
    exchange: str = Field(..., description="Internal exchange code (e.g., NASDAQ, NSE)")
    internal_id: str = Field(..., description="Platform-wide unique identifier (e.g., NSE:RELIANCE)")
    isin: Optional[str] = Field(None, description="International Securities Identification Number")
    
    # Future identifiers (FIGI, SEDOL, etc.) can be added here as Optional fields.

class InstrumentMetadata(BaseModel):
    """
    Generic trading metadata for an instrument.
    """
    name: str = Field(..., description="Full descriptive name of the instrument")
    currency: str = Field(..., description="ISO 4217 currency code (e.g., USD, INR)")
    tick_size: float = Field(..., description="Minimum price movement")
    lot_size: float = Field(default=1.0, description="Minimum trading quantity")
    price_precision: int = Field(default=2, description="Number of decimal places for price")
    quantity_precision: int = Field(default=0, description="Number of decimal places for quantity")
    
    status: InstrumentStatus = Field(default=InstrumentStatus.ACTIVE)
    listing_date: Optional[date] = Field(None, description="When the instrument was listed")
    delisting_date: Optional[date] = Field(None, description="When the instrument was or will be delisted")

class Instrument(BaseModel):
    """
    Base instrument representing the universal abstraction.
    """
    identity: InstrumentIdentity
    metadata: InstrumentMetadata
    instrument_type: InstrumentType

class Equity(Instrument):
    """Equity-specific representation."""
    instrument_type: InstrumentType = InstrumentType.EQUITY
    sector: Optional[str] = Field(None, description="Industry sector classification")
    industry: Optional[str] = Field(None, description="Specific industry classification")

class ETF(Instrument):
    """ETF-specific representation."""
    instrument_type: InstrumentType = InstrumentType.ETF
    underlying_index: Optional[str] = Field(None, description="Index the ETF tracks")

class Index(Instrument):
    """Index-specific representation."""
    instrument_type: InstrumentType = InstrumentType.INDEX
    
class FutureMetadata(Instrument):
    """Futures metadata representation (No pricing or greeks, just definition)."""
    instrument_type: InstrumentType = InstrumentType.FUTURE
    underlying_symbol: str = Field(..., description="The symbol of the underlying asset")
    expiration_date: date = Field(..., description="Expiration date of the contract")
    multiplier: float = Field(default=1.0, description="Contract multiplier")

class OptionMetadata(Instrument):
    """Options metadata representation (No pricing or greeks, just definition)."""
    instrument_type: InstrumentType = InstrumentType.OPTION
    underlying_symbol: str = Field(..., description="The symbol of the underlying asset")
    expiration_date: date = Field(..., description="Expiration date of the contract")
    strike_price: float = Field(..., description="Strike price")
    option_type: str = Field(..., description="'CALL' or 'PUT'")
    multiplier: float = Field(default=1.0, description="Contract multiplier")
