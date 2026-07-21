import uuid
from backend.risk_optimization_engine.models.statistics import OptimizationStatistics
from backend.risk_optimization_engine.contracts.metrics import IMetricsRepository

class StatisticsCollector:
    """
    Collects execution metrics and saves them to the metrics repository.
    """
    def __init__(self, metrics_repo: IMetricsRepository):
        self._metrics_repo = metrics_repo
        
    async def record_batch(
        self,
        cache_hits: int,
        cache_misses: int,
        total_snapshots: int,
        processing_time_ms: float,
        parallelism: bool,
        worker_count: int,
        batch_count: int
    ) -> None:
        
        reuse_percentage = (cache_hits / total_snapshots * 100.0) if total_snapshots > 0 else 0.0
        
        stats = OptimizationStatistics(
            batch_id=str(uuid.uuid4()),
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            total_snapshots=total_snapshots,
            reuse_percentage=reuse_percentage,
            processing_time_ms=processing_time_ms,
            parallelism=parallelism,
            worker_count=worker_count,
            batch_count=batch_count
        )
        
        await self._metrics_repo.save_statistics(stats)
