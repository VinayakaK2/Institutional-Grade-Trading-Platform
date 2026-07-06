"""
Historical Data Pipeline Exceptions
"""
from backend.core.exceptions import DomainException, InfrastructureException

class ProviderUnavailableException(InfrastructureException):
    """Raised when a historical data provider is unreachable or returns 5xx errors."""
    def __init__(self, provider_name: str, reason: str):
        super().__init__(
            message=f"Provider {provider_name} is unavailable: {reason}",
            details={"provider": provider_name, "reason": reason}
        )

class DownloadTimeoutException(InfrastructureException):
    """Raised when a download exceeds the maximum allowed time."""
    def __init__(self, symbol: str, provider_name: str):
        super().__init__(
            message=f"Download timed out for {symbol} from {provider_name}",
            details={"symbol": symbol, "provider": provider_name}
        )

class NormalizationException(DomainException):
    """Raised when raw data cannot be normalized into a canonical Candle."""
    def __init__(self, symbol: str, reason: str):
        super().__init__(
            message=f"Failed to normalize data for {symbol}: {reason}",
            error_code="NORMALIZATION_ERROR",
            details={"symbol": symbol, "reason": reason}
        )

class StorageException(InfrastructureException):
    """Raised when the storage pipeline fails to persist downloaded data."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Storage operation failed: {reason}",
            details={"reason": reason}
        )

class RateLimitException(InfrastructureException):
    """Raised when a provider's rate limit is exceeded."""
    def __init__(self, provider_name: str, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded for provider {provider_name}. Retry after {retry_after}s.",
            details={"provider": provider_name, "retry_after": retry_after}
        )
        self.retry_after = retry_after

class InvalidTimeframeException(DomainException):
    """Raised when an unsupported timeframe is requested from a provider."""
    def __init__(self, timeframe: str, provider_name: str):
        super().__init__(
            message=f"Timeframe {timeframe} is not supported by {provider_name}.",
            error_code="INVALID_TIMEFRAME",
            details={"timeframe": timeframe, "provider": provider_name}
        )
