class PositionRiskError(Exception):
    """Base exception for all Position Risk Engine errors."""
    pass

class PositionRiskValidationError(PositionRiskError):
    """Raised when structural or consistency validation fails."""
    pass

class PositionRiskConfigurationError(PositionRiskError):
    """Raised when the Position Risk Engine configuration is invalid or incompatible."""
    pass

class PositionRiskPipelineError(PositionRiskError):
    """Raised when the pipeline execution encounters a critical failure."""
    pass

class PositionRiskRepositoryError(PositionRiskError):
    """Raised when a repository operation fails."""
    pass

class PositionRiskImmutabilityError(PositionRiskError):
    """Raised when an attempt is made to mutate an immutable object or when snapshot lineage is broken."""
    pass
