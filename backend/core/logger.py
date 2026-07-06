"""
Logging Foundation (Phase 0)
Configures structlog for structured, context-aware JSON logging.
Includes masking of sensitive data and Correlation/Trace ID injection.
"""
import logging
import sys
from typing import Any, List
import structlog
from contextvars import ContextVar

# Context variables for distributed tracing and request correlation
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="UNKNOWN")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="UNKNOWN")

# Fields that should be masked in logs
SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "authorization"}

def mask_sensitive_data(logger: structlog.types.WrappedLogger, method_name: str, event_dict: structlog.types.EventDict) -> structlog.types.EventDict:
    """Masks sensitive data in the log event."""
    for key, value in event_dict.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "***MASKED***"
    return event_dict

def inject_context_ids(logger: structlog.types.WrappedLogger, method_name: str, event_dict: structlog.types.EventDict) -> structlog.types.EventDict:
    """Injects correlation and trace IDs into every log event."""
    event_dict["correlation_id"] = correlation_id_var.get()
    event_dict["trace_id"] = trace_id_var.get()
    return event_dict

def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configures the global logging architecture.
    Call this once at application startup.
    """
    level = logging.getLevelName(log_level.upper())
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    processors: List[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        inject_context_ids,
        mask_sensitive_data,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Returns a bound logger instance."""
    return structlog.get_logger(name)
