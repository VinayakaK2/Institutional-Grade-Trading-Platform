"""
Integration Tests for Metrics Framework
"""
from backend.infrastructure.metrics.registry import MetricsRegistry

def test_metrics_registry():
    registry = MetricsRegistry()
    counter = registry.create_counter("test_reqs", "Test requests")
    
    counter.inc()
    counter.inc(2)
    
    assert counter.value == 3
    
    gauge = registry.create_gauge("test_mem", "Test memory")
    gauge.set(100.5)
    gauge.inc(10.0)
    gauge.dec(5.0)
    
    assert gauge.value == 105.5
    
    hist = registry.create_histogram("test_time", "Test duration")
    hist.observe(1.2)
    hist.observe(0.8)
    
    assert hist.count == 2
    assert hist.sum == 2.0
    
    snapshot = registry.export()
    assert snapshot["test_reqs"] == 3
    assert snapshot["test_mem"] == 105.5
    assert snapshot["test_time"]["count"] == 2
