"""
Freshness Engine Domain Models
==============================

Domain models specific to the Freshness & Availability phase.
"""
from pydantic import BaseModel, ConfigDict
from backend.watchlist_engine.models.models import WatchlistSnapshot

class FreshWatchlistSnapshot(BaseModel):
    """
    Immutable, strictly-typed snapshot for the Fresh Candidate Watchlist.
    
    This wraps the generic WatchlistSnapshot via composition to preserve
    the Phase 6.1 boundary while attaching Freshness-specific lineage:
      - dataset_version
      - parent_candidate_watchlist_version
    
    IMMUTABILITY CONTRACT
    ---------------------
    WatchlistSnapshot is immutable.
    FreshWatchlistSnapshot owns only freshness-specific information.
    Neither object may mutate the other after creation.
    
    DATASET VERSION SEMANTICS
    -------------------------
    dataset_version refers to the certified canonical dataset version used 
    during freshness validation. If a new canonical dataset version is produced 
    later, a new FreshWatchlistSnapshot must be generated. 
    Existing snapshots must never be updated.
    
    SNAPSHOT LINEAGE
    ----------------
    FreshWatchlistSnapshot references exactly ONE immutable WatchlistSnapshot.
    The relationship is immutable for the lifetime of both snapshots.
    """
    model_config = ConfigDict(frozen=True)
    
    freshness_snapshot_id: str
    version: int
    watchlist_snapshot: WatchlistSnapshot
    dataset_version: str
    parent_candidate_watchlist_version: str
