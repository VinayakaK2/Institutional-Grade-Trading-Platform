class ConsolidationDetectionError(Exception):
    """Base exception for consolidation detection errors."""
    pass

class InvalidCandleDataError(ConsolidationDetectionError):
    """Raised when candle data is invalid (e.g., empty, duplicates, missing)."""
    pass

class ConsolidationRepositoryError(ConsolidationDetectionError):
    """Raised when a repository operation fails."""
    pass

class ConsolidationValidationError(ConsolidationDetectionError):
    """Raised when validation fails."""
    pass
