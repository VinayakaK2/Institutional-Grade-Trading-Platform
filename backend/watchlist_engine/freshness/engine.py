"""
Freshness & Availability Engine Orchestrator
============================================

Orchestrates the Freshness pipeline using the reusable WatchlistEngine foundation.
"""
import uuid
import time
from typing import Dict, Any

from backend.watchlist_engine.engine.engine import WatchlistEngine
from backend.watchlist_engine.models.models import WatchlistSnapshot
from backend.watchlist_engine.freshness.contracts import IFreshWatchlistRepository
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot


class FreshnessEngine:
    """
    Candidate Freshness & Availability Engine.
    
    This engine consumes a Candidate Watchlist snapshot, validates data freshness and 
    availability using a configured WatchlistEngine, and persists a strongly-typed
    FreshWatchlistSnapshot.
    """
    def __init__(
        self,
        watchlist_engine: WatchlistEngine,
        freshness_repository: IFreshWatchlistRepository,
        dataset_version: str
    ):
        """
        :param watchlist_engine: Reusable WatchlistEngine configured with Freshness pipeline.
        :param freshness_repository: Dedicated repository for persisting FreshWatchlistSnapshots.
        :param dataset_version: The required canonical dataset version for availability checks.
        """
        self._engine = watchlist_engine
        self._repository = freshness_repository
        self._dataset_version = dataset_version

    async def generate_fresh_watchlist(self, candidate_snapshot: WatchlistSnapshot) -> FreshWatchlistSnapshot:
        """
        Executes the freshness validation pipeline over the candidate watchlist.
        
        PIPELINE EXECUTION ORDER
        ------------------------
        The pipeline always executes in this strict order:
        1. Freshness Validation
        2. Availability Validation
        3. Dataset Integrity Validation
        
        Changing this order should require a pipeline version increment because 
        it may affect business output.
        
        Returns:
            A FreshWatchlistSnapshot wrapping the successfully validated candidates.
        """
        # Pass the dataset_version via shared_state so stages can access it
        shared_state: Dict[str, Any] = {
            "dataset_version": self._dataset_version
        }
        
        # Run the inner reusable engine
        # The engine will create its own generic WatchlistSnapshot and persist it 
        # to the generic WatchlistRepository.
        result = await self._engine.generate_watchlist(candidate_snapshot.candidates, shared_state)
        
        if not result.snapshot:
            raise RuntimeError("WatchlistEngine failed to generate a snapshot.")
            
        inner_snapshot = result.snapshot
        
        # Determine the next fresh version
        latest = await self._repository.load_latest_fresh_snapshot()
        next_version = (latest.version + 1) if latest else 1
        
        # Wrap via composition
        fresh_snapshot = FreshWatchlistSnapshot(
            freshness_snapshot_id=str(uuid.uuid4()),
            version=next_version,
            watchlist_snapshot=inner_snapshot,
            dataset_version=self._dataset_version,
            parent_candidate_watchlist_version=candidate_snapshot.candidate_selection_version or str(candidate_snapshot.version)
        )
        
        # Persist to our dedicated repository
        await self._repository.save_fresh_snapshot(fresh_snapshot)
        
        return fresh_snapshot
