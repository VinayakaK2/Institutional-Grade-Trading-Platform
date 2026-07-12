from backend.liquidity_grab_engine.models.models import LiquidityGrabExecutionContext

class ConsistencyValidator:
    """
    Validates logical consistency of the execution context.
    Focuses on dataset version alignment and lineage consistency.
    """
    
    @staticmethod
    def validate_lineage(context: LiquidityGrabExecutionContext) -> None:
        """
        Validates that the parent snapshots and dataset versions are structurally compatible.
        """
        if context.dataset_version <= 0:
            raise ValueError(f"Invalid dataset_version: {context.dataset_version}. Must be > 0.")
            
        if context.parent_trend_snapshot_version <= 0:
            raise ValueError(f"Invalid parent_trend_snapshot_version: {context.parent_trend_snapshot_version}. Must be > 0.")
            
        if context.parent_consolidation_snapshot_version <= 0:
            raise ValueError(f"Invalid parent_consolidation_snapshot_version: {context.parent_consolidation_snapshot_version}. Must be > 0.")
            
        # At this layer we check simple lineage constraints, e.g., configuration strict_mode.
        if context.configuration.validation.strict_mode:
            # We would typically inject dependencies to check if the parents actually exist in DB.
            # For Phase 9.1 orchestration layer without DB mocks, we just ensure values make sense.
            pass
