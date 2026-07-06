import logging
import time
from typing import Dict, Any
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

@dataclass
class OptimizationMetrics:
    total_execution_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    symbols_processed: int = 0
    batches_processed: int = 0
    total_indicators_calculated: int = 0

class OptimizationMetricsCollector:
    """
    Thread-safe collector for Indicator Optimization metrics.
    """
    def __init__(self):
        self._metrics = OptimizationMetrics()
        self._lock = threading.Lock()
        
    def record_execution_time(self, time_ms: float):
        with self._lock:
            self._metrics.total_execution_time_ms += time_ms
            
    def record_cache_hit(self, count: int = 1):
        with self._lock:
            self._metrics.cache_hits += count
            
    def record_cache_miss(self, count: int = 1):
        with self._lock:
            self._metrics.cache_misses += count
            
    def record_batch_processed(self, symbols_count: int, indicators_count: int):
        with self._lock:
            self._metrics.batches_processed += 1
            self._metrics.symbols_processed += symbols_count
            self._metrics.total_indicators_calculated += indicators_count
            
    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            hits = self._metrics.cache_hits
            misses = self._metrics.cache_misses
            total_cache_requests = hits + misses
            hit_rate = (hits / total_cache_requests * 100) if total_cache_requests > 0 else 0.0
            
            throughput = 0.0
            if self._metrics.total_execution_time_ms > 0:
                # symbols per second
                throughput = (self._metrics.symbols_processed / self._metrics.total_execution_time_ms) * 1000.0
                
            return {
                "execution_time_ms": round(self._metrics.total_execution_time_ms, 2),
                "cache_hits": hits,
                "cache_misses": misses,
                "cache_hit_rate_pct": round(hit_rate, 2),
                "symbols_processed": self._metrics.symbols_processed,
                "indicators_calculated": self._metrics.total_indicators_calculated,
                "throughput_symbols_per_sec": round(throughput, 2)
            }
            
    def log_metrics(self):
        metrics = self.get_metrics()
        logger.info(f"Optimization Metrics: {metrics}")

    def reset(self):
        with self._lock:
            self._metrics = OptimizationMetrics()
