from typing import Any

class DetectionStructuralValidator:
    """
    Validates structural integrity of the detection context.
    Ensures required sections and fields are populated and not null.
    """
    
    @staticmethod
    def validate(context: Any) -> None:
        if context is None:
            raise ValueError("Detection Context cannot be None.")
            
        if not hasattr(context, "dataset") or context.dataset is None:
            raise ValueError("dataset context is missing.")
            
        if not hasattr(context, "parent_snapshots") or context.parent_snapshots is None:
            raise ValueError("parent_snapshots context is missing.")
            
        if not hasattr(context, "market_data") or context.market_data is None:
            raise ValueError("market_data context is missing.")
            
        if not hasattr(context, "configuration") or context.configuration is None:
            raise ValueError("configuration is missing.")
            
        if not hasattr(context, "metadata") or context.metadata is None:
            raise ValueError("metadata is missing.")
            
        if context.market_data.symbol is None:
            raise ValueError("symbol is missing from market_data.")
            
        if context.market_data.timeframe is None:
            raise ValueError("timeframe is missing from market_data.")
            
        if context.market_data.candle_series is None:
            raise ValueError("candle_series is missing from market_data.")
