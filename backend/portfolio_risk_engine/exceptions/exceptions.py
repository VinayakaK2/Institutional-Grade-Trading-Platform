class PortfolioRiskError(Exception):
    """Base exception for all Portfolio Risk Engine errors."""
    pass

class PortfolioRiskValidationError(PortfolioRiskError):
    """Raised when structural or consistency validation fails."""
    pass

class PortfolioRiskConfigurationError(PortfolioRiskError):
    """Raised when the Portfolio Risk Engine configuration is invalid or incompatible."""
    pass

class PortfolioRiskPipelineError(PortfolioRiskError):
    """Raised when the pipeline execution encounters a critical failure."""
    pass

class PortfolioRiskRepositoryError(PortfolioRiskError):
    """Raised when a repository operation fails."""
    pass

class PortfolioRiskImmutabilityError(PortfolioRiskError):
    """Raised when an attempt is made to mutate an immutable object or when snapshot lineage is broken."""
    pass
