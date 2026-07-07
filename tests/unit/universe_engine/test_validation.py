import pytest
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment
from backend.universe_engine.validation.validators import UniverseValidator
from backend.universe_engine.models.config import ValidationSettings
from backend.universe_engine.models.exceptions import UniverseValidationError

def test_validate_symbols_success():
    settings = ValidationSettings()
    validator = UniverseValidator(settings)
    symbols = [
        UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False),
        UniverseInstrument(symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)
    ]
    
    # Should not raise any exceptions
    validator.validate_symbols(symbols)

def test_validate_symbols_duplicate():
    settings = ValidationSettings()
    validator = UniverseValidator(settings)
    symbols = [
        UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False),
        UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)
    ]
    
    with pytest.raises(UniverseValidationError) as exc:
        validator.validate_symbols(symbols)
    
    assert "Duplicate symbol detected" in str(exc.value)

def test_validate_symbols_empty_disallowed():
    settings = ValidationSettings(allow_empty_universe=False)
    validator = UniverseValidator(settings)
    
    with pytest.raises(UniverseValidationError) as exc:
        validator.validate_symbols([])
    
    assert "Universe is empty" in str(exc.value)

def test_validate_symbols_empty_allowed():
    settings = ValidationSettings(allow_empty_universe=True)
    validator = UniverseValidator(settings)
    
    # Should not raise exception
    validator.validate_symbols([])

def test_validate_symbols_null_symbol():
    settings = ValidationSettings()
    validator = UniverseValidator(settings)
    
    with pytest.raises(UniverseValidationError) as exc:
        validator.validate_symbols([None]) # type: ignore
        
    assert "Null instrument encountered" in str(exc.value)

def test_validate_symbols_whitespace_ticker():
    settings = ValidationSettings()
    validator = UniverseValidator(settings)
    symbols = [
        UniverseInstrument(symbol=SymbolReference(symbol="   ", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)
    ]
    
    with pytest.raises(UniverseValidationError) as exc:
        validator.validate_symbols(symbols)
        
    assert "Whitespace or empty ticker encountered" in str(exc.value)

