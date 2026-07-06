from enum import Enum
from datetime import date
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

from backend.market_data.models.symbol import SymbolReference

class ActionType(str, Enum):
    """Supported corporate action types."""
    STOCK_SPLIT = "STOCK_SPLIT"
    REVERSE_SPLIT = "REVERSE_SPLIT"
    BONUS_ISSUE = "BONUS_ISSUE"
    CASH_DIVIDEND = "CASH_DIVIDEND"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    SYMBOL_CHANGE = "SYMBOL_CHANGE"
    ISIN_CHANGE = "ISIN_CHANGE"
    DELISTING = "DELISTING"
    LISTING = "LISTING"

class ActionStatus(str, Enum):
    """Lifecycle states of a corporate action."""
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"

class CorporateAction(BaseModel):
    """Immutable corporate action representation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the action")
    symbol: SymbolReference = Field(..., description="The symbol affected by this action")
    action_type: ActionType = Field(..., description="The type of corporate action")
    effective_date: date = Field(..., description="The date the action takes effect")
    
    ratio: Optional[float] = Field(default=None, description="Ratio for splits/bonus (e.g. 3.0 for 3:1 split)")
    amount: Optional[float] = Field(default=None, description="Monetary amount for dividends")
    
    status: ActionStatus = Field(default=ActionStatus.PENDING, description="Current lifecycle state")
    
    metadata_info: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary metadata")
    
    model_config = {"frozen": False}
