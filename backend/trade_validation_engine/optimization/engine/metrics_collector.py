import time
from backend.trade_validation_engine.optimization.models.models import OptimizationStatistics

class OptimizationMetricsCollector:
    """
    Dedicated component to collect, aggregate, and measure all runtime timings 
    and statistics for observability.
    """
    def __init__(self):
        self._start_time = time.time()
        self.fingerprint_time_ms = 0
        self.cache_lookup_time_ms = 0
        self.parallel_execution_time_ms = 0
        self.merge_time_ms = 0
        self.persistence_time_ms = 0
        
        self.cache_hits = 0
        self.cache_misses = 0
        
        self.worker_count = 0
        self.batch_count = 0

    def get_statistics(self) -> OptimizationStatistics:
        total_time_ms = int((time.time() - self._start_time) * 1000)
        
        return OptimizationStatistics(
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            reused_validations=self.cache_hits,
            executed_validations=self.cache_misses,
            worker_count=self.worker_count,
            batch_count=self.batch_count,
            fingerprint_time_ms=self.fingerprint_time_ms,
            cache_lookup_time_ms=self.cache_lookup_time_ms,
            parallel_execution_time_ms=self.parallel_execution_time_ms,
            merge_time_ms=self.merge_time_ms,
            persistence_time_ms=self.persistence_time_ms,
            total_time_ms=total_time_ms
        )
