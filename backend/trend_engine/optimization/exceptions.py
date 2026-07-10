class TrendOptimizationError(Exception):
    """Base exception for all Trend Optimization errors."""
    pass

class OptimizationConfigurationError(TrendOptimizationError):
    """Raised when optimization configuration is invalid."""
    pass

class CacheInconsistencyError(TrendOptimizationError):
    """Raised when the cache returns invalid or mismatched results."""
    pass

class ParallelExecutionError(TrendOptimizationError):
    """Raised when parallel execution encounters an unrecoverable failure."""
    pass
