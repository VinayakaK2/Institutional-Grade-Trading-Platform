"""
Symbol Reference Model
"""
from pydantic import BaseModel, Field

class ExchangeReference(BaseModel):
    """Internal representation of a financial exchange."""
    code: str = Field(..., description="Internal exchange code (e.g., NSE, BSE, NASDAQ)")

class SymbolReference(BaseModel):
    """Internal representation of a tradable instrument."""
    symbol: str = Field(..., description="Internal symbol (e.g., RELIANCE, AAPL)")
    exchange: ExchangeReference
    
    @property
    def full_name(self) -> str:
        return f"{self.exchange.code}:{self.symbol}"
