import pytest
from backend.consolidation_engine.validation.validator import ConsolidationValidator
from backend.consolidation_engine.exceptions import ConsolidationValidationError
from backend.consolidation_engine.config.config import ConsolidationConfiguration

def test_validate_symbol():
    ConsolidationValidator.validate_symbol("AAPL:NASDAQ")
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_symbol("AAPL")
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_symbol("")

def test_validate_timeframe():
    ConsolidationValidator.validate_timeframe("1d")
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_timeframe("2d")

def test_validate_trend_snapshot():
    ConsolidationValidator.validate_trend_snapshot(1)
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_trend_snapshot(None)
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_trend_snapshot(0)

def test_validate_config():
    config = ConsolidationConfiguration(repository_batch_size=100)
    ConsolidationValidator.validate_config(config)
    
    bad_config = ConsolidationConfiguration(repository_batch_size=0)
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_config(bad_config)

def test_validate_execution_context():
    ConsolidationValidator.validate_execution_context(1, 1)
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_execution_context(0, 1)
    with pytest.raises(ConsolidationValidationError):
        ConsolidationValidator.validate_execution_context(1, 0)
