from typing import List
import asyncio
from backend.risk_optimization_engine.contracts.metrics import IMetricsRepository
from backend.risk_optimization_engine.models.statistics import OptimizationStatistics

class MemoryMetricsRepository(IMetricsRepository):
    def __init__(self) -> None:
        self._metrics: List[OptimizationStatistics] = []
        self._lock = asyncio.Lock()
        
    async def save_statistics(self, stats: OptimizationStatistics) -> None:
        async with self._lock:
            self._metrics.append(stats)
            
    async def get_all_statistics(self) -> List[OptimizationStatistics]:
        async with self._lock:
            return list(self._metrics)
