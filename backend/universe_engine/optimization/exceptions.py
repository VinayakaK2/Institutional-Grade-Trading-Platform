class OptimizationError(Exception):
    """Base exception for universe optimization errors."""
    pass

class DiffDetectionError(OptimizationError):
    """Raised when diff detection fails or is invalid."""
    pass

class BatchExecutionError(OptimizationError):
    """Raised when a parallel or sequential batch fails."""
    pass
