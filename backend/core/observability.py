"""
Observability Foundation (Phase 0)
Defines the architecture for health checks, metrics, and distributed tracing.
No actual infrastructure (Prometheus/DataDog/Jaeger) is instantiated here,
only the foundational abstractions that the application layer will use.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import time

# --- Health Check Architecture ---

def check_liveness() -> Dict[str, Any]:
    """
    Returns the basic liveness state of the application.
    Used by Kubernetes or load balancers to determine if the container should be restarted.
    Should be fast and not depend on external databases.
    """
    return {
        "status": "up",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def check_readiness() -> Dict[str, Any]:
    """
    Returns the readiness state of the application.
    Used by load balancers to determine if traffic should be routed here.
    Should check critical dependencies (Database, Redis, Message Queue).
    """
    # In Phase 1+, this will ping the DB and Cache.
    dependencies_healthy = True 
    
    if dependencies_healthy:
        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": {
                "database": "up",
                "redis": "up"
            }
        }
    else:
        # In a real framework, this would throw a specific Exception that maps to a 503 response.
        from backend.core.exceptions import InfrastructureException
        raise InfrastructureException(
            message="Service is not ready to accept traffic.",
            details={"database": "down"}
        )

# --- Metrics Architecture ---

class MetricsRegistry:
    """
    Abstract interface for recording application metrics.
    Actual implementation will use prometheus_client or OpenTelemetry in future phases.
    """
    
    @classmethod
    def increment_counter(cls, name: str, tags: Dict[str, str] = None) -> None:
        """Increments a counter (e.g., total_trades_executed)."""
        pass

    @classmethod
    def record_histogram(cls, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Records a distribution of values (e.g., api_latency_seconds)."""
        pass

    @classmethod
    def set_gauge(cls, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Sets a point-in-time value (e.g., active_connections)."""
        pass

# --- Tracing Architecture ---

def start_span(name: str) -> Any:
    """
    Placeholder for OpenTelemetry tracing.
    Wraps operations to measure latency and trace boundaries.
    """
    class DummySpan:
        def __init__(self, span_name: str):
            self.name = span_name
            self.start_time = 0
            
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.perf_counter() - self.start_time
            MetricsRegistry.record_histogram(f"{self.name}_duration_seconds", duration)
            
    return DummySpan(name)
