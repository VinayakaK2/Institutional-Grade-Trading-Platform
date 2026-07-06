from backend.core.observability import check_liveness, check_readiness, MetricsRegistry, start_span

def test_check_liveness():
    result = check_liveness()
    assert result["status"] == "up"

def test_check_readiness():
    result = check_readiness()
    assert result["status"] == "ready"

def test_metrics_registry():
    # Since these are dummy pass methods, we just call them to ensure no exception
    MetricsRegistry.increment_counter("test", {"tag": "val"})
    MetricsRegistry.record_histogram("test", 1.0, {"tag": "val"})
    MetricsRegistry.set_gauge("test", 10.0, {"tag": "val"})

def test_start_span():
    with start_span("test_span") as span:
        assert span.name == "test_span"
