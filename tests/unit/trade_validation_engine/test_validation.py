import pytest
from pydantic import ValidationError
from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.config.config import TradeValidationConfig
from backend.trade_validation_engine.validation.structural import TradeValidationStructuralValidator
from backend.trade_validation_engine.validation.consistency import TradeValidationConsistencyValidator
from backend.trade_validation_engine.exceptions.exceptions import InvalidExecutionContextError, SnapshotConsistencyError

def test_trade_validation_config_immutability():
    config = TradeValidationConfig()
    with pytest.raises(ValidationError):
        config.fail_fast = False

def test_structural_validator_valid_context():
    config = TradeValidationConfig()
    context = TradeValidationExecutionContext(
        symbol="BTCUSD",
        timeframe="1H",
        dataset_version=1,
        parent_watchlist_snapshot_version=1,
        parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1,
        parent_liquidity_grab_snapshot_version=1,
        configuration=config
    )
    # Should not raise
    TradeValidationStructuralValidator.validate(context)

def test_structural_validator_missing_symbol():
    config = TradeValidationConfig()
    context = TradeValidationExecutionContext(
        symbol="",
        timeframe="1H",
        dataset_version=1,
        parent_watchlist_snapshot_version=1,
        parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1,
        parent_liquidity_grab_snapshot_version=1,
        configuration=config
    )
    with pytest.raises(InvalidExecutionContextError, match="Context must have a valid symbol string."):
        TradeValidationStructuralValidator.validate(context)
        
def test_consistency_validator_invalid_version():
    config = TradeValidationConfig()
    context = TradeValidationExecutionContext(
        symbol="BTCUSD",
        timeframe="1H",
        dataset_version=1,
        parent_watchlist_snapshot_version=0,  # Invalid
        parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1,
        parent_liquidity_grab_snapshot_version=1,
        configuration=config
    )
    with pytest.raises(SnapshotConsistencyError, match="Watchlist version cannot be less than 1."):
        TradeValidationConsistencyValidator.validate(context)

def test_structural_validator_all_branches():
    config = TradeValidationConfig()
    
    # Missing timeframe
    with pytest.raises(InvalidExecutionContextError, match="timeframe"):
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))
        
    # Invalid dataset version
    with pytest.raises(InvalidExecutionContextError, match="dataset_version"):
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=0,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))
        
    # Invalid trend version
    with pytest.raises(InvalidExecutionContextError, match="parent_trend_snapshot_version"):
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=0,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))

    # Invalid consolidation version
    with pytest.raises(InvalidExecutionContextError, match="parent_consolidation_snapshot_version"):
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=0, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))

    # Invalid liquidity grab version
    with pytest.raises(InvalidExecutionContextError, match="parent_liquidity_grab_snapshot_version"):
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=0,
            configuration=config
        ))
        
    # Test None context
    with pytest.raises(InvalidExecutionContextError, match="cannot be null"):
        TradeValidationStructuralValidator.validate(None)
        
    # Test None configuration
    with pytest.raises(ValidationError): # Pydantic will actually catch this before our validator does if it's missing, but let's test if we hack it
        TradeValidationStructuralValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
            configuration=None
        ))
        
def test_consistency_validator_all_branches():
    config = TradeValidationConfig()
    
    with pytest.raises(SnapshotConsistencyError, match="Trend snapshot"):
        TradeValidationConsistencyValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=0,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))
        
    with pytest.raises(SnapshotConsistencyError, match="Consolidation snapshot"):
        TradeValidationConsistencyValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=0, parent_liquidity_grab_snapshot_version=1,
            configuration=config
        ))
        
    with pytest.raises(SnapshotConsistencyError, match="Liquidity Grab snapshot"):
        TradeValidationConsistencyValidator.validate(TradeValidationExecutionContext(
            symbol="BTCUSD", timeframe="1H", dataset_version=1,
            parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
            parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=0,
            configuration=config
        ))
