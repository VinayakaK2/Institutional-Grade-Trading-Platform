from backend.core.logger import mask_sensitive_data, inject_context_ids, setup_logging, correlation_id_var, trace_id_var, get_logger

def test_mask_sensitive_data():
    event_dict = {"password": "my_super_secret", "normal_key": "normal_value"}
    masked = mask_sensitive_data(None, "test_method", event_dict)
    assert masked["password"] == "***MASKED***"
    assert masked["normal_key"] == "normal_value"

def test_inject_context_ids():
    correlation_id_var.set("test-corr-id")
    trace_id_var.set("test-trace-id")
    event_dict = {}
    injected = inject_context_ids(None, "test_method", event_dict)
    assert injected["correlation_id"] == "test-corr-id"
    assert injected["trace_id"] == "test-trace-id"

def test_get_logger():
    setup_logging(log_level="DEBUG", log_format="json")
    logger = get_logger("test_module")
    assert logger is not None
