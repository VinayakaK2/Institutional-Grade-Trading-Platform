from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig

class VolumeAnalysisEngineContract(ABC):
    @abstractmethod
    def process_candles(self, candles: List[Candle], dataset_version: str, config: VolumeAnalysisConfig) -> Tuple[List[VolumeAnalysisResult], List[VolumeEvent]]:
        pass
