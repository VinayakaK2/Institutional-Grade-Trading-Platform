class PortfolioEngineError(Exception):
    """Base exception for all Portfolio Engine errors."""
    pass

class PortfolioPipelineError(PortfolioEngineError):
    """Raised when an infrastructure failure occurs during pipeline execution."""
    pass

class PortfolioRepositoryError(PortfolioEngineError):
    """Raised when a repository operation fails or violates invariants."""
    pass
