from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.market_data.models.candle import Candle
from backend.market_structure_engine.models.structure import MarketStructurePoint
from backend.market_structure_engine.models.events import StructureEvent
from backend.market_structure_engine.models.config import StructureConfig

class MarketStructureEngineContract(ABC):
    @abstractmethod
    def process_candles(self, candles: List[Candle], dataset_version: str, config: StructureConfig) -> Tuple[List[MarketStructurePoint], List[StructureEvent]]:
        """
        Orchestrates the entire market structure detection pipeline.
        1. Swing Detection (from SupportResistance engine)
        2. Structure Classification (HH/HL/LH/LL)
        3. Event Detection (BoS/ChoCH)
        4. Persistence
        """
        pass
