"""
Tests for Instrument models and strict typing.
"""
import pytest
from datetime import date
from pydantic import ValidationError
from backend.instrument.models.instrument import (
    InstrumentType,
    InstrumentStatus,
    InstrumentIdentity,
    InstrumentMetadata,
    Equity,
    FutureMetadata
)

@pytest.fixture
def base_identity():
    return InstrumentIdentity(
        symbol="RELIANCE",
        exchange="NSE",
        internal_id="NSE:RELIANCE",
        isin="INE002A01018"
    )

@pytest.fixture
def base_metadata():
    return InstrumentMetadata(
        name="Reliance Industries Limited",
        currency="INR",
        tick_size=0.05,
        lot_size=1.0,
        price_precision=2,
        quantity_precision=0,
        status=InstrumentStatus.ACTIVE,
        listing_date=date(1995, 1, 1)
    )

def test_instrument_identity_strictness():
    # Missing required field
    with pytest.raises(ValidationError):
        InstrumentIdentity(symbol="AAPL", exchange="NASDAQ") # missing internal_id

def test_equity_model_instantiation(base_identity, base_metadata):
    equity = Equity(
        identity=base_identity,
        metadata=base_metadata,
        sector="Energy",
        industry="Oil & Gas"
    )
    assert equity.instrument_type == InstrumentType.EQUITY
    assert equity.identity.internal_id == "NSE:RELIANCE"
    assert equity.metadata.tick_size == 0.05
    assert equity.sector == "Energy"

def test_future_model_instantiation(base_identity, base_metadata):
    # Adjust identity for future
    base_identity.symbol = "RELIANCE24JULFUT"
    future = FutureMetadata(
        identity=base_identity,
        metadata=base_metadata,
        underlying_symbol="RELIANCE",
        expiration_date=date(2024, 7, 25),
        multiplier=250.0
    )
    assert future.instrument_type == InstrumentType.FUTURE
    assert future.underlying_symbol == "RELIANCE"
    assert future.multiplier == 250.0
