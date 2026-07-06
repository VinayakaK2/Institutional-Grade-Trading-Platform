from abc import ABC, abstractmethod
from typing import List, Optional
from backend.market_structure_engine.models.structure import MarketStructurePoint
from backend.market_structure_engine.models.events import StructureEvent
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class MarketStructureRepositoryContract(ABC):
    @abstractmethod
    def save_structure_points(self, points: List[MarketStructurePoint], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> None:
        pass

    @abstractmethod
    def save_structure_events(self, events: List[StructureEvent], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> None:
        pass

    @abstractmethod
    def get_structure_points(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[MarketStructurePoint]:
        """
        Retrieves historical structure points ordered chronologically (oldest first or newest first, must be consistent).
        Let's enforce: chronological order (oldest first).
        """
        pass

    @abstractmethod
    def get_structure_events(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[StructureEvent]:
        """
        Retrieves historical events ordered chronologically (oldest first).
        """
        pass
