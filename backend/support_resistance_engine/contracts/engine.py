from abc import ABC, abstractmethod
from typing import List
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.support_resistance_engine.models.zone import SwingPoint, Zone

class SwingDetectorContract(ABC):
    @abstractmethod
    def detect_swings(self, candles: List[Candle]) -> List[SwingPoint]:
        pass

class ZoneGeneratorContract(ABC):
    @abstractmethod
    def generate_zones(self, swings: List[SwingPoint], symbol: SymbolReference, timeframe: Timeframe, dataset_version: str) -> List[Zone]:
        pass

class ZoneLifecycleContract(ABC):
    @abstractmethod
    def update_zones(self, active_zones: List[Zone], new_candles: List[Candle]) -> List[Zone]:
        pass
        
    @abstractmethod
    def merge_zones(self, zones: List[Zone]) -> List[Zone]:
        """
        Merges overlapping zones of the same type.
        
        Merge Behaviour:
        - The new center is calculated as the average of the two overlapping zones' centers.
        - The boundaries are expanded to encompass both zones (highest upper, lowest lower).
        - Touch and rejection counts are summed together.
        - The newer zone's ID and source swing point are typically preserved or a new ID is generated.
        """
        pass

class SupportResistanceEngineContract(ABC):
    @abstractmethod
    def process_candles(self, candles: List[Candle], dataset_version: str) -> List[Zone]:
        pass
