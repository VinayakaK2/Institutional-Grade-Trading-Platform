class PositionSizingError(Exception):
    """Base exception for all Position Sizing Engine errors."""
    pass

class PositionSizingValidationError(PositionSizingError):
    """Raised when structural or consistency validation fails."""
    pass

class PositionSizingConfigurationError(PositionSizingError):
    """Raised when the Position Sizing Engine configuration is invalid or incompatible."""
    pass

class PositionSizingPipelineError(PositionSizingError):
    """Raised when the pipeline execution encounters a critical failure."""
    pass

class PositionSizingRepositoryError(PositionSizingError):
    """Raised when a repository operation fails."""
    pass

class PositionSizingImmutabilityError(PositionSizingError):
    """Raised when an attempt is made to mutate an immutable object or when snapshot lineage is broken."""
    pass
