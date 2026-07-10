class CertificationFailure(Exception):
    """Raised when any certification stage fails."""
    pass

class DeterminismError(CertificationFailure):
    """Raised when deterministic execution produces inconsistent outputs."""
    pass

class ImmutabilityViolationError(CertificationFailure):
    """Raised when the certification framework attempts to mutate an existing production object."""
    pass

class CertificationConfigurationError(CertificationFailure):
    """Raised when certification configuration is invalid."""
    pass
