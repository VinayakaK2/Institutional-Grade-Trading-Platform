import pytest
from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.candidate_selection.ordering import SymbolNameOrderingStrategy

def test_symbol_name_ordering_strategy() -> None:
    strategy = SymbolNameOrderingStrategy()
    
    candidates = [
        WatchlistCandidate(watchlist_symbol=WatchlistSymbol(symbol=SymbolReference(symbol="Z", exchange=ExchangeReference(code="NYSE")))),
        WatchlistCandidate(watchlist_symbol=WatchlistSymbol(symbol=SymbolReference(symbol="A", exchange=ExchangeReference(code="NYSE")))),
        WatchlistCandidate(watchlist_symbol=WatchlistSymbol(symbol=SymbolReference(symbol="M", exchange=ExchangeReference(code="NYSE")))),
    ]
    
    ordered = strategy.order(candidates)
    
    assert [c.watchlist_symbol.symbol.symbol for c in ordered] == ["A", "M", "Z"]
