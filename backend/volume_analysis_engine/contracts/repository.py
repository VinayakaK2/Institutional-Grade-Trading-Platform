from abc import ABC, abstractmethod
from typing import List, Optional
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.volume_analysis_engine.models.volume import VolumeAnalysisResult, VolumeEvent

class VolumeAnalysisRepositoryContract(ABC):
    @abstractmethod
    def save_analysis(self, results: List[VolumeAnalysisResult], events: List[VolumeEvent]) -> None:
        pass

    @abstractmethod
    def get_analysis_results(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[VolumeAnalysisResult]:
        pass

    @abstractmethod
    def get_events(self, symbol: SymbolReference, timeframe: Timeframe, dataset_version: str, limit: Optional[int] = None) -> List[VolumeEvent]:
        pass
