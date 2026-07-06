"""
Candle Storage Exceptions
Integrates with Phase 0 Exception Framework.
"""
from backend.core.exceptions import InfrastructureException, DomainException

class CandleStorageException(InfrastructureException):
    def __init__(self, message: str, details: dict = None):
        # InfrastructureException hardcodes error_code="INFRASTRUCTURE_ERROR"
        super().__init__(
            message=message,
            details=details
        )

class CandleQueryException(DomainException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            error_code="CANDLE_QUERY_ERROR",
            details=details
        )
