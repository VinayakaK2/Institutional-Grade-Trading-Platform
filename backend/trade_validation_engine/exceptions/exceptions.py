class TradeValidationError(Exception):
    """Base exception for all Trade Validation Engine errors."""
    pass

class InvalidExecutionContextError(TradeValidationError):
    """Raised when the execution context is invalid (e.g. missing required snapshots)."""
    pass

class ValidationPipelineError(TradeValidationError):
    """Raised when an error occurs during pipeline execution."""
    pass

class SnapshotConsistencyError(TradeValidationError):
    """Raised when the upstream snapshots are inconsistent (e.g. timeframe mismatch)."""
    pass

class RepositoryError(TradeValidationError):
    """Raised when a repository operation fails."""
    pass
