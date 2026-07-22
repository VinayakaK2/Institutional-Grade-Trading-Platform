class PortfolioCorrelationEngineError(Exception):
    """Base exception for Portfolio Correlation Engine errors."""
    pass

class PortfolioCorrelationValidationError(PortfolioCorrelationEngineError):
    """Raised when validation rules fail."""
    pass

class PortfolioCorrelationPipelineError(PortfolioCorrelationEngineError):
    """Raised when an infrastructure failure occurs during pipeline execution."""
    pass

class PortfolioCorrelationRepositoryError(PortfolioCorrelationEngineError):
    """Raised when a repository operation fails or violates invariants."""
    pass
