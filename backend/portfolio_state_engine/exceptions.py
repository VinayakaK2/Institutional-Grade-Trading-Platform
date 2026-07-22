class PortfolioStateEngineError(Exception):
    """Base exception for Portfolio State Engine errors."""
    pass

class PortfolioStateValidationError(PortfolioStateEngineError):
    """Raised when validation rules fail (if fail_fast is enabled)."""
    pass

class PortfolioStatePipelineError(PortfolioStateEngineError):
    """Raised when an infrastructure failure occurs during pipeline execution."""
    pass

class PortfolioStateRepositoryError(PortfolioStateEngineError):
    """Raised when a repository operation fails or violates invariants."""
    pass
