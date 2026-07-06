"""
Tests for Registry Validation Engine.
"""
import pytest
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.models.instrument import InstrumentIdentity, InstrumentMetadata, Equity
from backend.instrument.registry.validation import RegistryValidator
from backend.instrument.exceptions import (
    DuplicateSymbolException,
    InvalidExchangeException,
    InvalidMetadataException
)

@pytest.fixture
def validator():
    return RegistryValidator()

@pytest.fixture
def dummy_exchange():
    return ExchangeMetadata(code="NSE", name="NSE", country_code="IN", timezone="Asia/Kolkata")

@pytest.fixture
def dummy_instrument():
    identity = InstrumentIdentity(symbol="TEST", exchange="NSE", internal_id="NSE:TEST")
    metadata = InstrumentMetadata(name="Test", currency="INR", tick_size=0.05, lot_size=1)
    return Equity(identity=identity, metadata=metadata)

def test_validate_exchanges_duplicate(validator):
    ex = ExchangeMetadata(code="NSE", name="NSE", country_code="IN", timezone="Asia/Kolkata")
    # Sending two identical exchanges in the same batch
    with pytest.raises(InvalidExchangeException):
        validator.validate_exchanges([ex, ex])

def test_validate_instruments_unknown_exchange(validator, dummy_instrument):
    validator.set_active_exchanges([]) # No active exchanges
    with pytest.raises(InvalidExchangeException):
        validator.validate_instruments([dummy_instrument])

def test_validate_instruments_duplicate_in_registry(validator, dummy_instrument, dummy_exchange):
    validator.set_active_exchanges([dummy_exchange])
    # Assume 'NSE:TEST' is already in registry
    with pytest.raises(DuplicateSymbolException):
        validator.validate_instruments([dummy_instrument], existing_ids={"NSE:TEST"})

def test_validate_instruments_duplicate_in_batch(validator, dummy_instrument, dummy_exchange):
    validator.set_active_exchanges([dummy_exchange])
    # Sending the same instrument twice in a batch
    with pytest.raises(DuplicateSymbolException):
        validator.validate_instruments([dummy_instrument, dummy_instrument])

def test_validate_instruments_invalid_metadata(validator, dummy_instrument, dummy_exchange):
    validator.set_active_exchanges([dummy_exchange])
    dummy_instrument.metadata.tick_size = -1.0 # Invalid
    with pytest.raises(InvalidMetadataException):
        validator.validate_instruments([dummy_instrument])
