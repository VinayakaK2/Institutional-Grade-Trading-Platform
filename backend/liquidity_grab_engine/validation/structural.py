from typing import Any

class StructuralValidator:
    """
    Validates structural integrity of the execution context and configuration.
    Focuses on required fields, type validation, and null checks.
    """
    
    @staticmethod
    def validate_context(context: Any) -> None:
        """
        Validates the context object fundamentally exists and satisfies Pydantic validation.
        The LiquidityGrabExecutionContext handles most type validation internally via Pydantic.
        """
        if context is None:
            raise ValueError("Execution context cannot be None.")
            
        if not hasattr(context, "symbol") or context.symbol is None:
            raise ValueError("Symbol is missing from execution context.")
            
        if not hasattr(context, "timeframe") or context.timeframe is None:
            raise ValueError("Timeframe is missing from execution context.")
            
        if not hasattr(context, "dataset_version") or context.dataset_version is None:
            raise ValueError("dataset_version is missing from execution context.")
            
        if not hasattr(context, "parent_trend_snapshot_version") or context.parent_trend_snapshot_version is None:
            raise ValueError("parent_trend_snapshot_version is missing from execution context.")
            
        if not hasattr(context, "parent_consolidation_snapshot_version") or context.parent_consolidation_snapshot_version is None:
            raise ValueError("parent_consolidation_snapshot_version is missing from execution context.")
            
        if not hasattr(context, "configuration") or context.configuration is None:
            raise ValueError("Configuration is missing from execution context.")
            
        if not hasattr(context, "metadata") or context.metadata is None:
            raise ValueError("Metadata is missing from execution context.")
