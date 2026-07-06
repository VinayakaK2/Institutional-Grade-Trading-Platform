"""
Validation Pipeline
Provides a standardized way to execute multiple validation rules against an input.
"""
from typing import Protocol, TypeVar, List, Any, Optional
from backend.application.validation.exceptions import BusinessValidationException

T = TypeVar("T", contravariant=True)

class ValidationRule(Protocol[T]):
    """Abstract protocol for a single validation rule."""
    
    async def validate(self, target: T) -> Optional[str]:
        """
        Evaluates the rule against the target.
        Returns an error message string if validation fails, otherwise None.
        """
        ...


class ValidationPipeline:
    """Executes a series of validation rules."""
    
    def __init__(self) -> None:
        self._rules: List[ValidationRule] = []
        
    def add_rule(self, rule: ValidationRule) -> "ValidationPipeline":
        """Adds a rule to the pipeline."""
        self._rules.append(rule)
        return self
        
    async def execute(self, target: Any) -> None:
        """
        Executes all rules against the target.
        Raises BusinessValidationException if any rules fail.
        Collects all errors before failing (Aggregate behavior).
        """
        errors = []
        for rule in self._rules:
            error = await rule.validate(target)
            if error:
                errors.append(error)
                
        if errors:
            raise BusinessValidationException(
                message=f"Validation failed with {len(errors)} errors.",
                errors=errors
            )
