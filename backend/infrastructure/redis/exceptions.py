"""
Redis Exceptions
Defines exceptions specific to Redis operations.
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class RedisConnectionException(InfrastructureException):
    """Raised when the application fails to connect to Redis."""
    def __init__(self, message: str = "Failed to connect to Redis.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "REDIS_CONNECTION_ERROR"

class RedisOperationException(InfrastructureException):
    """Raised when a specific Redis operation (get, set, del) fails."""
    def __init__(self, message: str = "Redis operation failed.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "REDIS_OPERATION_ERROR"
