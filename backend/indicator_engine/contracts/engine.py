from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorQueryFilters

class IndicatorQueryEngineContract(ABC):
    """
    Contract for retrieving calculated indicators.
    """
    
    @abstractmethod
    def query(self, filters: IndicatorQueryFilters) -> AsyncGenerator[IndicatorResult, None]:
        pass

class IndicatorCalculationEngineContract(ABC):
    """
    Contract for the core Indicator Engine orchestration.
    """
    
    @abstractmethod
    async def process_batch(self, candles: List[Candle], dataset_version: str) -> None:
        """
        Processes a batch of candles against all registered calculators,
        and saves the resulting indicators.
        Supports incremental updates (e.g., if only one candle is new, it 
        should figure out how to calculate it).
        """
        pass
