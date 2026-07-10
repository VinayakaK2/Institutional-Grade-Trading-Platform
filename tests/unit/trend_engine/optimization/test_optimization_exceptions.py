import pytest
from backend.trend_engine.optimization.exceptions import (
    TrendOptimizationError,
    OptimizationConfigurationError,
    CacheInconsistencyError,
    ParallelExecutionError
)

def test_optimization_exceptions():
    """
    Lightweight test to ensure custom exceptions can be raised
    and instantiated correctly, providing coverage.
    """
    with pytest.raises(TrendOptimizationError):
        raise TrendOptimizationError("base error")
        
    with pytest.raises(OptimizationConfigurationError):
        raise OptimizationConfigurationError("config error")
        
    with pytest.raises(CacheInconsistencyError):
        raise CacheInconsistencyError("cache error")
        
    with pytest.raises(ParallelExecutionError):
        raise ParallelExecutionError("parallel error")
