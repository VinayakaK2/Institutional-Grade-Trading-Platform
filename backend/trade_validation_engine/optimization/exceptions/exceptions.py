class OptimizationError(Exception):
    """Base exception for optimization layer errors."""
    pass

class OptimizationCacheError(OptimizationError):
    """Raised when repository/cache operations fail."""
    pass

class OptimizationConcurrencyError(OptimizationError):
    """Raised when async parallel execution fails or is cancelled (e.g. fail_fast)."""
    pass
