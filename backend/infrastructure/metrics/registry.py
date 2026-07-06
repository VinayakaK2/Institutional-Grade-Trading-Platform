"""
Metrics Registry
Central hub for registering and exporting metrics.
"""
from typing import Dict, Any, cast
from backend.infrastructure.metrics.instruments import Counter, Gauge, Histogram, Metric
from backend.core.logger import get_logger

logger = get_logger(__name__)

class MetricsRegistry:
    """Manages the lifecycle and storage of all application metrics."""
    
    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        
    def create_counter(self, name: str, description: str) -> Counter:
        if name not in self._metrics:
            self._metrics[name] = Counter(name, description)
        return cast(Counter, self._metrics[name])
        
    def create_gauge(self, name: str, description: str) -> Gauge:
        if name not in self._metrics:
            self._metrics[name] = Gauge(name, description)
        return cast(Gauge, self._metrics[name])
        
    def create_histogram(self, name: str, description: str) -> Histogram:
        if name not in self._metrics:
            self._metrics[name] = Histogram(name, description)
        return cast(Histogram, self._metrics[name])

    def export(self) -> Dict[str, Any]:
        """Returns a snapshot of current metrics."""
        report: Dict[str, Any] = {}
        for name, metric in self._metrics.items():
            if isinstance(metric, Counter) or isinstance(metric, Gauge):
                report[name] = metric.value
            elif isinstance(metric, Histogram):
                report[name] = {"count": metric.count, "sum": metric.sum}
        return report

# Global Metrics Registry
metrics_registry = MetricsRegistry()
