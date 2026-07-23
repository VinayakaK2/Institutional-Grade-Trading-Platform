class PaperExecutionQualityError(Exception):
    """Base exception for all Paper Execution Quality Engine errors."""
    pass

class PaperExecutionQualityValidationError(PaperExecutionQualityError):
    """Raised when context fails structural validation."""
    pass

class PaperExecutionQualityConsistencyError(PaperExecutionQualityError):
    """Raised when context fails consistency validation (e.g., missing parent snapshot)."""
    pass

class PaperExecutionQualityCalculationError(PaperExecutionQualityError):
    """Raised when an invalid calculation state is detected (e.g., NaN/Infinity or invalid bounds)."""
    pass

class PaperExecutionQualityPersistenceError(PaperExecutionQualityError):
    """Raised when there is an issue persisting the execution quality snapshot."""
    pass
