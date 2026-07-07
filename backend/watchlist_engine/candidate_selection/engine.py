"""
Candidate Selection Engine
==========================

Serves as the entry point for generating the daily watchlist.
Coordinates loading the CandidateUniverseView, maps symbols to WatchlistCandidate,
and delegates pipeline execution to the WatchlistEngine.
"""
from typing import Optional
import hashlib

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistEngine
from backend.watchlist_engine.candidate_selection.config import CandidateSelectionSettings
from backend.universe_engine.contracts.query import ICandidateUniverseQueryService
from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistSymbol, WatchlistResult
from backend.watchlist_engine.models.exceptions import WatchlistConfigurationError

logger = get_logger(__name__)


class CandidateSelectionEngine:
    """
    Orchestrator for the Phase 6.2 Candidate Selection process.
    
    Responsibilities:
    - Load the universe view from Phase 5 (via ICandidateUniverseQueryService).
    - Map Universe items to WatchlistCandidate objects.
    - Invoke WatchlistEngine to execute the filtering pipeline and persist the snapshot.
    """

    def __init__(
        self,
        universe_query_service: ICandidateUniverseQueryService,
        watchlist_engine: IWatchlistEngine,
        settings: CandidateSelectionSettings
    ):
        self._universe_query = universe_query_service
        self._watchlist_engine = watchlist_engine
        self._settings = settings
        self._selection_version = "1.0.0"

    async def generate_candidate_watchlist(
        self, 
        run_id: str, 
        universe_version: Optional[int] = None
    ) -> WatchlistResult:
        """
        Executes candidate selection against the Universe.
        
        Args:
            run_id: Unique execution identifier.
            universe_version: If provided, loads a specific universe version.
                              Otherwise, loads the latest.
        """
        logger.info(f"Generating Candidate Watchlist [Run ID: {run_id}]")
        
        # 1. Load Universe View
        if universe_version is not None:
            universe_view = await self._universe_query.load_by_version(universe_version)
        else:
            universe_view = await self._universe_query.load_latest()
            
        if not universe_view:
            raise WatchlistConfigurationError(
                message="Failed to load CandidateUniverseView. No universe found.",
                details={"requested_version": universe_version}
            )
            
        if not universe_view.symbols:
            raise WatchlistConfigurationError(
                message="Loaded CandidateUniverseView is empty.",
                details={"universe_snapshot_id": universe_view.universe_snapshot_id}
            )
            
        logger.info(f"Loaded Universe Snapshot {universe_view.universe_snapshot_id} (Version {universe_view.universe_version}) with {len(universe_view.symbols)} symbols.")

        # 2. Map to WatchlistCandidates
        candidates = []
        for sym in universe_view.symbols:
            # We must map the structural fields into WatchlistSymbol, and 
            # pass boolean flags into stage_metadata for CandidateSelectionStage to use.
            wl_symbol = WatchlistSymbol(
                symbol=sym.symbol,
                market_segment=sym.exchange,
                instrument_type=sym.instrument_type,
            )
            
            candidate = WatchlistCandidate(
                watchlist_symbol=wl_symbol,
                stage_metadata={
                    "is_active": sym.is_active,
                    "is_certified": sym.is_certified
                }
            )
            candidates.append(candidate)
            
        # 3. Calculate Config Hash for tracking
        config_hash_input = f"{self._settings.candidate_limit}_{self._settings.default_ordering}_{','.join(self._settings.always_include)}_{','.join(self._settings.always_exclude)}"
        config_hash = hashlib.sha256(config_hash_input.encode("utf-8")).hexdigest()[:16]

        # 4. Delegate to WatchlistEngine
        return await self._watchlist_engine.generate_watchlist(
            run_id=run_id,
            candidates=candidates,
            source_universe_snapshot_id=universe_view.universe_snapshot_id,
            source_universe_version=universe_view.universe_version,
            config_hash=config_hash,
            candidate_selection_version=self._selection_version
        )
