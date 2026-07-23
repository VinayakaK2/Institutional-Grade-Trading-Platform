class PaperFillError(Exception):
    """Base exception for all Paper Fill Engine errors."""
    pass

class PaperFillValidationError(PaperFillError):
    """Raised when a fill context fails structural validation."""
    pass

class PaperFillConsistencyError(PaperFillError):
    """Raised when a fill context fails consistency validation (e.g., missing parent snapshot, not ACCEPTED)."""
    pass

class PaperFillTransitionError(PaperFillError):
    """Raised when an invalid state transition is attempted."""
    pass

class PaperFillPersistenceError(PaperFillError):
    """Raised when there is an issue persisting the fill snapshot."""
    pass

class PaperFillSimulationError(PaperFillError):
    """Raised when an invalid simulation state is detected (e.g., overfill)."""
    pass
