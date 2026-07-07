class LiquidityFilterError(Exception):
    """Base exception for Liquidity Filter Engine errors."""
    pass

class LiquidityConfigurationError(LiquidityFilterError):
    """Raised when liquidity filter configuration is invalid."""
    pass

class MissingLiquidityDataError(LiquidityFilterError):
    """Raised when required data (candles, market cap) cannot be fetched."""
    pass

class LiquidityRepositoryError(LiquidityFilterError):
    """Raised when liquidity universe cannot be persisted or loaded."""
    pass
