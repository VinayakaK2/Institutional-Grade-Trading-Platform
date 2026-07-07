class UniverseClassificationError(Exception):
    """Base exception for classification errors."""
    pass

class UnknownSectorError(UniverseClassificationError):
    """Raised when a sector cannot be resolved and no fallback is permitted."""
    pass

class UnknownIndustryError(UniverseClassificationError):
    """Raised when an industry cannot be resolved and no fallback is permitted."""
    pass

class ClassificationDataMissingError(UniverseClassificationError):
    """Raised when mandatory provider data is missing."""
    pass

class LiquidityMetricsMissingError(UniverseClassificationError):
    """Raised when expected parent liquidity metrics are missing."""
    pass
