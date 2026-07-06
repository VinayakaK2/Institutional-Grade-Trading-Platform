"""
Tests for Exchange models and validation.
"""
import pytest
from pydantic import ValidationError
from backend.instrument.models.exchange import ExchangeMetadata

def test_exchange_metadata_creation():
    exchange = ExchangeMetadata(
        code="NSE",
        name="National Stock Exchange",
        country_code="IN",
        timezone="Asia/Kolkata"
    )
    assert exchange.code == "NSE"
    assert exchange.name == "National Stock Exchange"
    assert exchange.country_code == "IN"
    assert exchange.timezone == "Asia/Kolkata"
    assert exchange.is_active is True

def test_exchange_metadata_missing_fields():
    with pytest.raises(ValidationError):
        ExchangeMetadata(
            code="NSE",
            name="National Stock Exchange"
            # Missing country_code and timezone
        )
