from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from backend.support_resistance_engine.models.zone import Zone
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class SupportResistanceRepositoryContract(ABC):
    @abstractmethod
    def save_zones(self, zones: List[Zone]) -> None:
        pass
        
    @abstractmethod
    def update_zones(self, zones: List[Zone]) -> None:
        pass

class SupportResistanceQueryContract(ABC):
    @abstractmethod
    def get_active_zones(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> List[Zone]:
        """
        Retrieves all active zones for a given symbol, timeframe, and dataset version.
        
        Ordering:
        Zones returned MUST be deterministically ordered.
        The default enforced ordering is newest first (created_at DESC).
        """
        pass
        
    @abstractmethod
    def get_historical_zones(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Zone]:
        pass
        
    @abstractmethod
    def get_nearest_zones(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        dataset_version: str, 
        current_price: float, 
        limit: int = 1
    ) -> List[Zone]:
        """Returns the nearest support and resistance zones."""
        pass
