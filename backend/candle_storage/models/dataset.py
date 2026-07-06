"""
Candle Storage Models
Defines dataset types and query filters for explicit candle access.
"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe


class DatasetType(str, Enum):
    """
    Explicitly defines the dataset to query or mutate.
    """
    RAW = "raw"
    CANONICAL = "canonical"
    ADJUSTED = "adjusted"


class CandleQueryFilters(BaseModel):
    """
    Standardized query filters for fetching historical candles.
    """
    symbol: SymbolReference = Field(..., description="The instrument symbol")
    timeframe: Timeframe = Field(..., description="The candle timeframe")
    dataset_type: DatasetType = Field(..., description="The explicit dataset to query against")
    
    # Must be provided if dataset_type == DatasetType.ADJUSTED
    dataset_version: Optional[str] = Field(None, description="The version of the adjusted dataset")
    
    start_time: Optional[datetime] = Field(None, description="Inclusive start time")
    end_time: Optional[datetime] = Field(None, description="Inclusive end time")
    
    limit: Optional[int] = Field(None, gt=0, description="Maximum number of candles to return")
    order_by_desc: bool = Field(False, description="If True, order by timestamp descending")

    def validate_dataset_requirements(self):
        """Ensures that query inputs align with the required dataset type."""
        if self.dataset_type == DatasetType.ADJUSTED and not self.dataset_version:
            raise ValueError("Dataset version must be provided when querying ADJUSTED dataset.")
        
        if self.dataset_type != DatasetType.ADJUSTED and self.dataset_version:
            raise ValueError(f"Dataset version should not be provided for {self.dataset_type.value} dataset.")
