from abc import ABC, abstractmethod
from typing import List
from backend.market_structure_engine.models.structure import MarketStructurePoint
from backend.market_structure_engine.models.events import StructureEvent
from backend.market_structure_engine.models.config import StructureConfig
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.models.zone import SwingPoint

class StructureAnalyzerContract(ABC):
    @abstractmethod
    def classify_swings(self, swings: List[SwingPoint], previous_structure: List[MarketStructurePoint]) -> List[MarketStructurePoint]:
        """
        Classifies incoming swing points into HH, HL, LH, LL based on previous structure.
        Must enforce chronological ordering and reject invalid transitions or duplicate/missing swings.
        """
        pass

class EventDetectorContract(ABC):
    @abstractmethod
    def detect_events(
        self, 
        structure_points: List[MarketStructurePoint], 
        candles: List[Candle], 
        config: StructureConfig,
        previous_events: List[StructureEvent]
    ) -> List[StructureEvent]:
        """
        Detects Break of Structure (BoS) and Change of Character (ChoCH) based on structural points and price action.
        """
        pass
