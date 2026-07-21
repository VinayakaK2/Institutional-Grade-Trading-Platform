class RiskDecisionValidationError(Exception):
    """
    Exception raised when Structural or Consistency validation fails.
    """
    pass

class RiskDecisionBuilderError(Exception):
    """
    Exception raised during snapshot hash building.
    """
    pass
