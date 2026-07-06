"""
Market Data Exceptions
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class MarketDataException(InfrastructureException):
    """Base exception for all market data errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "MARKET_DATA_ERROR"

class ProviderOfflineException(MarketDataException):
    """Raised when a specific provider is unreachable or times out repeatedly."""
    def __init__(self, provider_name: str, message: str = "Provider offline.") -> None:
        super().__init__(message=message, details={"provider": provider_name})
        self.error_code = "PROVIDER_OFFLINE"

class AllProvidersFailedException(MarketDataException):
    """Raised when the primary and all failover providers fail to serve a request."""
    def __init__(self, message: str = "All market data providers failed.") -> None:
        super().__init__(message=message)
        self.error_code = "ALL_PROVIDERS_FAILED"

class RateLimitExceededException(MarketDataException):
    """Raised when the API rate limit is exceeded."""
    def __init__(self, provider_name: str, message: str = "Rate limit exceeded.") -> None:
        super().__init__(message=message, details={"provider": provider_name})
        self.error_code = "RATE_LIMIT_EXCEEDED"

class InvalidSymbolException(MarketDataException):
    """Raised when the requested symbol does not exist on the provider."""
    def __init__(self, symbol: str, provider_name: str, message: str = "Invalid symbol.") -> None:
        super().__init__(message=message, details={"symbol": symbol, "provider": provider_name})
        self.error_code = "INVALID_SYMBOL"

class DataNormalizationException(MarketDataException):
    """Raised when the provider's raw data cannot be normalized (corrupted/missing fields)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "NORMALIZATION_ERROR"
