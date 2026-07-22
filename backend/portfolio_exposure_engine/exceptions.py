class PortfolioExposureEngineError(Exception):
    """Base exception for Portfolio Exposure Engine errors."""
    pass

class PortfolioExposureValidationError(PortfolioExposureEngineError):
    """Raised when validation rules fail (if fail_fast is enabled)."""
    pass

class PortfolioExposurePipelineError(PortfolioExposureEngineError):
    """Raised when an infrastructure failure occurs during pipeline execution."""
    pass

class PortfolioExposureRepositoryError(PortfolioExposureEngineError):
    """Raised when a repository operation fails or violates invariants."""
    pass
