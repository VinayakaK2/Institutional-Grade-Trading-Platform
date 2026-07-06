from abc import ABC, abstractmethod
from typing import List
from backend.market_data.models.candle import Candle
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent
from backend.volume_analysis_engine.models.config import VolumeAnalysisConfig

class AverageVolumeCalculatorContract(ABC):
    @abstractmethod
    def calculate(self, candles: List[Candle], config: VolumeAnalysisConfig) -> List[float]:
        pass

class RelativeVolumeAnalyzerContract(ABC):
    @abstractmethod
    def analyze(self, candles: List[Candle], avg_volumes: List[float], dataset_version: str, config: VolumeAnalysisConfig) -> List[VolumeAnalysisResult]:
        pass

class VolumeClassifierContract(ABC):
    @abstractmethod
    def classify(self, results: List[VolumeAnalysisResult], config: VolumeAnalysisConfig) -> List[VolumeAnalysisResult]:
        """Classifies RVOL as NORMAL, HIGH, LOW based on thresholds. (This can be merged into Analyzer if needed, but separated per request)"""
        pass

class VolumeEventDetectorContract(ABC):
    @abstractmethod
    def detect_events(
        self, 
        candles: List[Candle], 
        analysis_results: List[VolumeAnalysisResult], 
        config: VolumeAnalysisConfig,
        previous_events: List[VolumeEvent]
    ) -> List[VolumeEvent]:
        pass
