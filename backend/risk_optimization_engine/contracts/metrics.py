from abc import ABC, abstractmethod
from typing import List
from backend.risk_optimization_engine.models.statistics import OptimizationStatistics

class IMetricsRepository(ABC):
    """
    Repository for saving collected optimization statistics.
    """
    
    @abstractmethod
    async def save_statistics(self, stats: OptimizationStatistics) -> None:
        pass
        
    @abstractmethod
    async def get_all_statistics(self) -> List[OptimizationStatistics]:
        pass
