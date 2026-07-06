"""
Tests for Search Engine.
"""
import pytest
from backend.instrument.models.instrument import Equity, InstrumentIdentity, InstrumentMetadata
from backend.instrument.search.index import SearchIndex
from backend.instrument.search.query import SearchQueryEngine
from backend.instrument.contracts.search import SearchCriteria

@pytest.fixture
def index():
    return SearchIndex()

@pytest.fixture
def query_engine(index):
    return SearchQueryEngine(index)

@pytest.fixture
def sample_instruments():
    aapl = Equity(
        identity=InstrumentIdentity(symbol="AAPL", exchange="NASDAQ", internal_id="NASDAQ:AAPL", isin="US0378331005"),
        metadata=InstrumentMetadata(name="Apple Inc", currency="USD", tick_size=0.01)
    )
    rel = Equity(
        identity=InstrumentIdentity(symbol="RELIANCE", exchange="NSE", internal_id="NSE:RELIANCE", isin="INE002A01018"),
        metadata=InstrumentMetadata(name="Reliance Industries", currency="INR", tick_size=0.05)
    )
    return [aapl, rel]

def test_search_index_rebuild(index, sample_instruments):
    index.rebuild(sample_instruments)
    assert len(index.instruments) == 2
    assert "NASDAQ:AAPL" in index.by_symbol["AAPL"]
    assert "NSE:RELIANCE" in index.by_isin["INE002A01018"]
    assert "NASDAQ:AAPL" in index.prefix_name["app"]
    assert "NASDAQ:AAPL" in index.prefix_name["appl"]
    assert "NASDAQ:AAPL" in index.prefix_name["apple"]

def test_search_by_exact_symbol(query_engine, index, sample_instruments):
    index.rebuild(sample_instruments)
    results = query_engine.search(SearchCriteria(query="AAPL", exact_match=True))
    assert len(results) == 1
    assert results[0] == "NASDAQ:AAPL"

def test_search_by_isin(query_engine, index, sample_instruments):
    index.rebuild(sample_instruments)
    results = query_engine.search(SearchCriteria(query="INE002A01018", exact_match=True))
    assert len(results) == 1
    assert results[0] == "NSE:RELIANCE"

def test_search_by_prefix(query_engine, index, sample_instruments):
    index.rebuild(sample_instruments)
    # Prefix matches symbol and name
    results = query_engine.search(SearchCriteria(query="App", exact_match=False))
    assert len(results) == 1
    assert results[0] == "NASDAQ:AAPL"
    
    results = query_engine.search(SearchCriteria(query="Reli", exact_match=False))
    assert len(results) == 1
    assert results[0] == "NSE:RELIANCE"

def test_search_by_exchange(query_engine, index, sample_instruments):
    index.rebuild(sample_instruments)
    results = query_engine.search(SearchCriteria(exchange="NSE"))
    assert len(results) == 1
    assert results[0] == "NSE:RELIANCE"
    
def test_search_empty_criteria(query_engine, index, sample_instruments):
    index.rebuild(sample_instruments)
    results = query_engine.search(SearchCriteria())
    assert len(results) == 0
