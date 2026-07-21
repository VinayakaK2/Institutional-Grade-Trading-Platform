class RiskEngineError(Exception):
    """Base exception for all Risk Engine errors."""
    pass

class RiskValidationError(RiskEngineError):
    """Raised when structural or consistency validation fails."""
    pass

class RiskConfigurationError(RiskEngineError):
    """Raised when the Risk Engine configuration is invalid or incompatible."""
    pass

class RiskPipelineError(RiskEngineError):
    """Raised when the pipeline execution encounters a critical failure."""
    pass

class RiskRepositoryError(RiskEngineError):
    """Raised when a repository operation fails."""
    pass

class RiskImmutabilityError(RiskEngineError):
    """Raised when an attempt is made to mutate an immutable object or when snapshot lineage is broken."""
    pass
