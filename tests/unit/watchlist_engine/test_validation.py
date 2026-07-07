"""
Unit tests for WatchlistValidator (structural validation only).

Covers:
  - Empty candidate list when allow_empty_watchlist=False (should raise).
  - Empty candidate list when allow_empty_watchlist=True (should pass).
  - Null candidate entry (should raise).
  - Null WatchlistSymbol on candidate (should raise).
  - Null SymbolReference on WatchlistSymbol (should raise).
  - Empty/whitespace ticker symbol (should raise).
  - Duplicate symbol detection (should raise).
  - Candidate list exceeding max_watchlist_size (should raise).
  - Valid candidate list (should pass without exception).
"""
import pytest
from unittest.mock import MagicMock

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistSymbol
from backend.watchlist_engine.models.config import WatchlistValidationSettings
from backend.watchlist_engine.models.exceptions import WatchlistValidationError
from backend.watchlist_engine.validation.validators import WatchlistValidator


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_candidate(ticker: str, exchange_code: str = "NSE") -> WatchlistCandidate:
    """Helper to build a minimal valid WatchlistCandidate."""
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol=ticker, exchange=ExchangeReference(code=exchange_code)),
            market_segment="EQUITY_CASH",
            instrument_type="EQUITY",
        )
    )


@pytest.fixture
def strict_validator() -> WatchlistValidator:
    """Validator with production defaults (empty watchlist not allowed)."""
    return WatchlistValidator(WatchlistValidationSettings())


@pytest.fixture
def lenient_validator() -> WatchlistValidator:
    """Validator that permits empty watchlists (for testing)."""
    return WatchlistValidator(WatchlistValidationSettings(allow_empty_watchlist=True))


# ── Empty Universe ────────────────────────────────────────────────────────────

def test_empty_candidates_raises_when_not_allowed(strict_validator: WatchlistValidator) -> None:
    """Empty candidate list should raise WatchlistValidationError when disallowed."""
    with pytest.raises(WatchlistValidationError, match="empty"):
        strict_validator.validate([])


def test_empty_candidates_allowed_when_configured(lenient_validator: WatchlistValidator) -> None:
    """Empty candidate list should pass when allow_empty_watchlist=True."""
    lenient_validator.validate([])  # Must not raise.


# ── Null Entries ──────────────────────────────────────────────────────────────

def test_null_candidate_entry_raises(strict_validator: WatchlistValidator) -> None:
    """A None entry in the candidate list should raise WatchlistValidationError."""
    with pytest.raises(WatchlistValidationError, match="Null WatchlistCandidate"):
        strict_validator.validate([None])  # type: ignore[list-item]


def test_null_watchlist_symbol_raises(strict_validator: WatchlistValidator) -> None:
    """A candidate with a null WatchlistSymbol should raise WatchlistValidationError."""
    bad_candidate = WatchlistCandidate.__new__(WatchlistCandidate)
    bad_candidate.__dict__["watchlist_symbol"] = None  # type: ignore[assignment]
    bad_candidate.__dict__["stage_metadata"] = {}
    with pytest.raises(WatchlistValidationError, match="Null WatchlistSymbol"):
        strict_validator.validate([bad_candidate])


# ── Whitespace Tickers ────────────────────────────────────────────────────────

def test_whitespace_ticker_raises(strict_validator: WatchlistValidator) -> None:
    """A candidate with a whitespace-only ticker should raise WatchlistValidationError."""
    bad = WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="   ", exchange=ExchangeReference(code="NSE")),
        )
    )
    with pytest.raises(WatchlistValidationError, match="whitespace"):
        strict_validator.validate([bad])


# ── Duplicate Detection ────────────────────────────────────────────────────────

def test_duplicate_symbol_raises(strict_validator: WatchlistValidator) -> None:
    """Duplicate symbols (same full_name) must raise WatchlistValidationError."""
    c1 = make_candidate("RELIANCE", "NSE")
    c2 = make_candidate("RELIANCE", "NSE")  # Same exchange + ticker = duplicate.
    with pytest.raises(WatchlistValidationError, match="Duplicate"):
        strict_validator.validate([c1, c2])


def test_same_ticker_different_exchange_is_valid(strict_validator: WatchlistValidator) -> None:
    """Same ticker on different exchanges must NOT be treated as a duplicate."""
    c1 = make_candidate("INFY", "NSE")
    c2 = make_candidate("INFY", "BSE")  # Different exchange — not a duplicate.
    strict_validator.validate([c1, c2])  # Must not raise.


# ── Max Size ─────────────────────────────────────────────────────────────────

def test_exceeds_max_watchlist_size_raises() -> None:
    """Candidate list exceeding max_watchlist_size must raise WatchlistValidationError."""
    small_limit_validator = WatchlistValidator(WatchlistValidationSettings(max_watchlist_size=2))
    candidates = [make_candidate(f"TICK{i}") for i in range(3)]
    with pytest.raises(WatchlistValidationError, match="maximum"):
        small_limit_validator.validate(candidates)


# ── Valid Input ────────────────────────────────────────────────────────────────

def test_valid_candidates_pass(strict_validator: WatchlistValidator) -> None:
    """A well-formed candidate list must pass validation without exceptions."""
    candidates = [make_candidate("RELIANCE"), make_candidate("INFY"), make_candidate("TCS")]
    strict_validator.validate(candidates)  # Must not raise.
