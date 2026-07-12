from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.exceptions.exceptions import InvalidExecutionContextError

class TradeValidationStructuralValidator:
    """
    Validates structural integrity of the Trade Validation Context.
    Checks for required fields, nulls, types, and configuration presence.
    """
    
    @staticmethod
    def validate(context: TradeValidationExecutionContext) -> None:
        """
        Validates the structure of the context.
        Raises InvalidExecutionContextError if validation fails.
        """
        if not context:
            raise InvalidExecutionContextError("TradeValidationExecutionContext cannot be null.")
            
        if not context.symbol or not isinstance(context.symbol, str) or context.symbol.strip() == "":
            raise InvalidExecutionContextError("Context must have a valid symbol string.")
            
        if not context.timeframe or not isinstance(context.timeframe, str) or context.timeframe.strip() == "":
            raise InvalidExecutionContextError("Context must have a valid timeframe string.")
            
        if not isinstance(context.dataset_version, int) or context.dataset_version <= 0:
            raise InvalidExecutionContextError("Context must have a dataset_version greater than 0.")
            
        if not isinstance(context.parent_watchlist_snapshot_version, int) or context.parent_watchlist_snapshot_version <= 0:
            raise InvalidExecutionContextError("Context must have a parent_watchlist_snapshot_version greater than 0.")
            
        if not isinstance(context.parent_trend_snapshot_version, int) or context.parent_trend_snapshot_version <= 0:
            raise InvalidExecutionContextError("Context must have a parent_trend_snapshot_version greater than 0.")
            
        if not isinstance(context.parent_consolidation_snapshot_version, int) or context.parent_consolidation_snapshot_version <= 0:
            raise InvalidExecutionContextError("Context must have a parent_consolidation_snapshot_version greater than 0.")
            
        if not isinstance(context.parent_liquidity_grab_snapshot_version, int) or context.parent_liquidity_grab_snapshot_version <= 0:
            raise InvalidExecutionContextError("Context must have a parent_liquidity_grab_snapshot_version greater than 0.")
            
        if not context.configuration:
            raise InvalidExecutionContextError("Context must contain a TradeValidationConfig.")
