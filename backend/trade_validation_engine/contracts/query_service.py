from abc import ABC, abstractmethod
from typing import List, Optional
from backend.trade_validation_engine.models.models import TradeValidationSnapshot

class ITradeValidationQueryService(ABC):
    """
    Contract for the read-only Query Service.
    No domain logic or modification abilities.
    """
    
    @abstractmethod
    async def get_by_id(self, snapshot_id: str) -> Optional[TradeValidationSnapshot]:
        """
        Gets a snapshot by its exact validation ID.
        """
        pass
        
    @abstractmethod
    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[TradeValidationSnapshot]:
        """
        Gets the most recent snapshot for a given symbol and timeframe.
        """
        pass
        
    @abstractmethod
    async def get_by_snapshot_version(self, symbol: str, timeframe: str, version_key: str, version_val: int) -> List[TradeValidationSnapshot]:
        """
        Gets snapshots matching a specific parent snapshot version.
        (e.g. all validation snapshots where parent_trend_snapshot_version == 5)
        """
        pass
        
    @abstractmethod
    async def list_paginated(self, symbol: str, limit: int = 50, offset: int = 0) -> List[TradeValidationSnapshot]:
        """
        Lists snapshots for a symbol with basic pagination.
        """
        pass
