"""
Watchlist Validator
====================

Structural validation of the WatchlistCandidate list.

Rules enforced (structural only — no business logic):
  1. Empty candidate list (unless allow_empty_watchlist=True).
  2. None/null candidate entries.
  3. Null SymbolReference inside WatchlistSymbol.
  4. Duplicate symbols (same full_name within a single candidate list).
  5. Empty or whitespace symbol tickers.
  6. Candidate list exceeding max_watchlist_size.

Rules NEVER enforced here:
  - Liquidity thresholds
  - Trend or momentum filters
  - Ranking or scoring criteria
  - Trading session validity
  - Any business rule whatsoever
"""
from typing import List

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistValidator
from backend.watchlist_engine.models.models import WatchlistCandidate
from backend.watchlist_engine.models.config import WatchlistValidationSettings
from backend.watchlist_engine.models.exceptions import WatchlistValidationError

logger = get_logger(__name__)


class WatchlistValidator(IWatchlistValidator):
    """
    Default structural validator for the Watchlist Engine.

    Enforces structural integrity rules against the candidate list.
    Raises WatchlistValidationError on the first violation encountered.
    """

    def __init__(self, settings: WatchlistValidationSettings) -> None:
        self._settings = settings

    def validate(self, candidates: List[WatchlistCandidate]) -> None:
        """
        Validates the candidate list for structural correctness.

        Args:
            candidates: List of WatchlistCandidate objects to validate.

        Raises:
            WatchlistValidationError: If any structural validation rule is violated.
        """
        # Rule 1: Empty list check.
        if not candidates and not self._settings.allow_empty_watchlist:
            raise WatchlistValidationError(
                "Watchlist candidate list is empty, but allow_empty_watchlist is False.",
                details={"allow_empty_watchlist": self._settings.allow_empty_watchlist},
            )

        # Rule 2: Max size guard.
        if len(candidates) > self._settings.max_watchlist_size:
            raise WatchlistValidationError(
                f"Candidate list size ({len(candidates)}) exceeds the maximum "
                f"allowed watchlist size ({self._settings.max_watchlist_size}).",
                details={
                    "candidate_count": len(candidates),
                    "max_watchlist_size": self._settings.max_watchlist_size,
                },
            )

        seen_symbols: set = set()

        for idx, candidate in enumerate(candidates):
            # Rule 3: Null candidate entry.
            if candidate is None:
                raise WatchlistValidationError(
                    f"Null WatchlistCandidate encountered at index {idx}.",
                    details={"index": idx},
                )

            # Rule 4: Null WatchlistSymbol.
            if candidate.watchlist_symbol is None:
                raise WatchlistValidationError(
                    f"Null WatchlistSymbol encountered on candidate at index {idx}.",
                    details={"index": idx},
                )

            # Rule 5: Null or invalid SymbolReference.
            symbol_ref = candidate.watchlist_symbol.symbol
            if symbol_ref is None:
                raise WatchlistValidationError(
                    f"Null SymbolReference on candidate at index {idx}.",
                    details={"index": idx},
                )

            # Rule 6: Empty or whitespace ticker.
            ticker = symbol_ref.symbol
            if not ticker or not ticker.strip():
                raise WatchlistValidationError(
                    f"Empty or whitespace symbol ticker encountered at index {idx}.",
                    details={"index": idx},
                )

            # Rule 7: Duplicate symbol detection.
            full_name = symbol_ref.full_name
            if full_name in seen_symbols:
                raise WatchlistValidationError(
                    f"Duplicate symbol detected: '{full_name}'.",
                    details={"duplicate_symbol": full_name, "index": idx},
                )
            seen_symbols.add(full_name)

        logger.debug(
            f"Watchlist structural validation passed for {len(candidates)} candidates."
        )
