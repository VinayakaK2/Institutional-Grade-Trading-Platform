from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.exceptions.exceptions import SnapshotConsistencyError

class TradeValidationConsistencyValidator:
    """
    Validates logical consistency of the Trade Validation Context.
    Ensures that the upstream snapshots form a coherent state.
    """
    
    @staticmethod
    def validate(context: TradeValidationExecutionContext) -> None:
        """
        Validates the consistency of the context.
        Raises SnapshotConsistencyError if validation fails.
        """
        # In a real scenario, this validator might check that parent snapshot IDs match the requested timeframe/symbol
        # Since we just have the versions in the context, we make sure they are logically sound.
        
        # Here we just perform baseline consistency checks that can be derived from the context itself.
        if context.parent_watchlist_snapshot_version < 1:
            raise SnapshotConsistencyError("Watchlist version cannot be less than 1.")
            
        if context.parent_trend_snapshot_version < 1:
            raise SnapshotConsistencyError("Trend snapshot version cannot be less than 1.")
            
        if context.parent_consolidation_snapshot_version < 1:
            raise SnapshotConsistencyError("Consolidation snapshot version cannot be less than 1.")
            
        if context.parent_liquidity_grab_snapshot_version < 1:
            raise SnapshotConsistencyError("Liquidity Grab snapshot version cannot be less than 1.")
