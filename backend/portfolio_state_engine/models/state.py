from typing import List
from pydantic import BaseModel, Field

class OpenPosition(BaseModel):
    """Represents a single open position."""
    symbol: str
    quantity: float
    average_entry_price: float
    current_price: float
    sector: str = "Unknown"
    industry: str = "Unknown"
    
    model_config = {"frozen": True}

class PendingOrder(BaseModel):
    """Represents a single pending order."""
    order_id: str
    symbol: str
    order_type: str
    quantity: float
    target_price: float
    
    model_config = {"frozen": True}

class CapitalSummary(BaseModel):
    """Represents portfolio capital."""
    available_capital: float
    used_capital: float
    cash_balance: float
    
    model_config = {"frozen": True}

class PnLSummary(BaseModel):
    """Represents portfolio profit and loss."""
    realized_pnl: float
    unrealized_pnl: float
    
    model_config = {"frozen": True}

class PortfolioState(BaseModel):
    """
    A strongly-typed sub-model representing all business fields.
    """
    positions: List[OpenPosition] = Field(default_factory=list)
    pending_orders: List[PendingOrder] = Field(default_factory=list)
    capital: CapitalSummary = Field(
        default_factory=lambda: CapitalSummary(available_capital=0.0, used_capital=0.0, cash_balance=0.0)
    )
    pnl: PnLSummary = Field(
        default_factory=lambda: PnLSummary(realized_pnl=0.0, unrealized_pnl=0.0)
    )
    
    model_config = {"frozen": True}
