from typing import Optional
from backend.consolidation_engine.exceptions import ConsolidationValidationError
from backend.consolidation_engine.config.config import ConsolidationConfiguration

class ConsolidationValidator:
    """
    Structural validation for Consolidation Engine inputs.
    """
    
    @staticmethod
    def validate_symbol(symbol: str) -> None:
        if not symbol or ":" not in symbol:
            raise ConsolidationValidationError(f"Invalid symbol format: {symbol}. Expected format like 'AAPL:NASDAQ'.")

    @staticmethod
    def validate_timeframe(timeframe: str) -> None:
        valid_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
        if timeframe not in valid_timeframes:
            raise ConsolidationValidationError(f"Invalid timeframe: {timeframe}.")

    @staticmethod
    def validate_trend_snapshot(trend_snapshot_version: Optional[int]) -> None:
        if trend_snapshot_version is None or trend_snapshot_version <= 0:
            raise ConsolidationValidationError("Trend snapshot version is missing or invalid.")
            
    @staticmethod
    def validate_config(config: ConsolidationConfiguration) -> None:
        if config.repository_batch_size <= 0:
            raise ConsolidationValidationError("Repository batch size must be positive.")
            
    @staticmethod
    def validate_execution_context(dataset_version: int, trend_snapshot_version: int) -> None:
        if dataset_version <= 0:
            raise ConsolidationValidationError("Dataset version must be positive.")
        if trend_snapshot_version <= 0:
            raise ConsolidationValidationError("Trend snapshot version must be positive.")
