"""
Candidate Selection Pipeline Stages.

Executes strictly in the following order:
1. ManualIncludeStage
2. CandidateSelectionStage
3. ManualExcludeStage
"""
import time
from typing import Set

from backend.watchlist_engine.contracts.contracts import IWatchlistStage
from backend.watchlist_engine.models.models import (
    WatchlistExecutionContext,
    WatchlistStageResult,
    WatchlistStageStatus
)
from backend.watchlist_engine.models.exceptions import WatchlistValidationError
from backend.watchlist_engine.candidate_selection.config import CandidateSelectionSettings
from backend.watchlist_engine.candidate_selection.ordering import get_ordering_strategy


class ManualIncludeStage(IWatchlistStage):
    """
    Validates and applies manual inclusion overrides.
    
    Rules:
    - If a symbol in always_include is in the universe, it is marked with is_manual_include=True.
    - If a symbol is missing from the universe, it raises a WatchlistValidationError.
      (The engine must NEVER manufacture market instruments).
    """
    def __init__(self, settings: CandidateSelectionSettings):
        self._settings = settings

    @property
    def name(self) -> str:
        return "ManualIncludeStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.perf_counter()
        
        always_include_set = set(self._settings.always_include)
        found_symbols: Set[str] = set()

        for candidate in context.candidates:
            symbol_ticker = candidate.watchlist_symbol.symbol.symbol
            if symbol_ticker in always_include_set:
                candidate.stage_metadata["is_manual_include"] = True
                found_symbols.add(symbol_ticker)
            else:
                candidate.stage_metadata["is_manual_include"] = False

        missing_symbols = always_include_set - found_symbols
        if missing_symbols:
            raise WatchlistValidationError(
                message=f"Manual inclusion failed: Symbols not found in universe: {missing_symbols}",
                details={"missing_symbols": list(missing_symbols)}
            )
            
        context.metadata["manual_include_count"] = len(found_symbols)

        duration_ms = (time.perf_counter() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={"included_symbols": list(found_symbols)}
        )


class CandidateSelectionStage(IWatchlistStage):
    """
    Filters, sorts, and limits candidates based on objective criteria.
    
    Rules:
    - Keeps symbols that are ACTIVE and CERTIFIED (or flagged as manual include).
    - Sorts using the configured ordering strategy.
    - Limits to candidate_limit. Manual includes bypass truncation logic by 
      consuming slots but are never truncated themselves if they fit in the limit.
      Actually, we just prioritize them or sort them all and take top N. 
      The requirement says: "Manual overrides... Always Include". 
      If we limit to N, and an Always Include is at index N+1 after sorting,
      does it get cut? If it's "Always Include", it shouldn't get cut.
      Therefore, we prioritize manual includes.
    """
    def __init__(self, settings: CandidateSelectionSettings):
        self._settings = settings
        self._ordering_strategy = get_ordering_strategy(settings.default_ordering)

    @property
    def name(self) -> str:
        return "CandidateSelectionStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.perf_counter()

        # Filter
        filtered_candidates = []
        for candidate in context.candidates:
            is_manual_include = candidate.stage_metadata.get("is_manual_include", False)
            
            # Read properties from the boundary model / stage_metadata mapped by Orchestrator
            is_active = candidate.stage_metadata.get("is_active", False)
            is_certified = candidate.stage_metadata.get("is_certified", False)
            
            if is_manual_include or (is_active and is_certified):
                filtered_candidates.append(candidate)

        # Sort
        sorted_candidates = self._ordering_strategy.order(filtered_candidates)

        # Apply Limit, ensuring manual includes are preserved
        manual_includes = [c for c in sorted_candidates if c.stage_metadata.get("is_manual_include", False)]
        regular_candidates = [c for c in sorted_candidates if not c.stage_metadata.get("is_manual_include", False)]
        
        limit = self._settings.candidate_limit
        
        # If manual includes exceed the limit, we just take them up to limit or allow limit breach?
        # The prompt says: "Configurable Candidate Limit". We'll respect the limit.
        final_candidates = manual_includes[:limit]
        remaining_slots = limit - len(final_candidates)
        
        if remaining_slots > 0:
            final_candidates.extend(regular_candidates[:remaining_slots])

        # Final sort to ensure final output is perfectly ordered even after split-merge
        context.candidates = self._ordering_strategy.order(final_candidates)

        duration_ms = (time.perf_counter() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={
                "initial_count": len(filtered_candidates),
                "final_count": len(context.candidates),
                "limit_applied": limit
            }
        )


class ManualExcludeStage(IWatchlistStage):
    """
    Removes candidates specified in the manual exclusion list.
    """
    def __init__(self, settings: CandidateSelectionSettings):
        self._settings = settings

    @property
    def name(self) -> str:
        return "ManualExcludeStage"

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        start_time = time.perf_counter()
        
        always_exclude_set = set(self._settings.always_exclude)
        excluded_symbols = []

        final_candidates = []
        for candidate in context.candidates:
            symbol_ticker = candidate.watchlist_symbol.symbol.symbol
            if symbol_ticker in always_exclude_set:
                excluded_symbols.append(symbol_ticker)
            else:
                final_candidates.append(candidate)

        context.candidates = final_candidates
        context.metadata["manual_exclude_count"] = len(excluded_symbols)

        duration_ms = (time.perf_counter() - start_time) * 1000
        return WatchlistStageResult(
            stage_name=self.name,
            status=WatchlistStageStatus.SUCCESS,
            duration_ms=duration_ms,
            metadata={"excluded_symbols": excluded_symbols}
        )
