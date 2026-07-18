class ValidationRulesError(Exception):
    """Base exception for the Validation Rules Engine."""
    pass

class RuleExecutionError(ValidationRulesError):
    """Raised when an individual rule crashes unexpectedly."""
    pass

class ValidationRepositoryError(ValidationRulesError):
    """Raised for persistence and retrieval failures in the repository."""
    pass

class ValidationPipelineError(ValidationRulesError):
    """Raised for failures occurring at the pipeline orchestration layer."""
    pass
