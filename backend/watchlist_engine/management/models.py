from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from backend.market_data.models.symbol import SymbolReference
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot

class WatchlistStatus(str, Enum):
    """
    Status of a managed watchlist snapshot.
    Per user directive, this is restricted to VALID only.
    """
    VALID = "VALID"

class WatchlistAuditRecord(BaseModel):
    """
    Audit trail for state-changing events.
    """
    model_config = ConfigDict(frozen=True)

    event_id: str
    managed_snapshot_id: str
    event_type: str
    timestamp: datetime
    metadata: Dict[str, Any]

class ManagedWatchlistSnapshot(BaseModel):
    """
    Immutable representation of a fully managed and verified watchlist snapshot.
    
    This snapshot owns the lineage, deterministic business fingerprint, and 
    composes the FreshWatchlistSnapshot containing the actual candidates.
    """
    model_config = ConfigDict(frozen=True)
    
    managed_snapshot_id: str
    version: int
    
    # Composed inner snapshot (which wraps the base WatchlistSnapshot)
    fresh_watchlist_snapshot: FreshWatchlistSnapshot
    
    # Lineage Metadata (elevated for fast indexing/retrieval)
    parent_fresh_watchlist_version: int
    parent_candidate_watchlist_version: str
    parent_universe_version: int
    dataset_version: str
    pipeline_version: str
    config_hash: str
    
    # Business fingerprint (Symbol IDs + Dataset Version + Config Hash)
    business_fingerprint: str
    
    created_at: datetime
    status: WatchlistStatus

class WatchlistDiffSummary(BaseModel):
    """
    Summary statistics for a diff between two snapshots.
    """
    model_config = ConfigDict(frozen=True)
    
    added_count: int
    removed_count: int
    unchanged_count: int

class WatchlistDiff(BaseModel):
    """
    Deterministic comparison between two snapshots.
    
    Note: WatchlistDiffs are dynamically generated and NEVER persisted to the database.
    """
    model_config = ConfigDict(frozen=True)
    
    base_version: Optional[int]
    target_version: int
    
    added_symbols: List[WatchlistSymbol]
    removed_symbols: List[WatchlistSymbol]
    unchanged_symbols: List[WatchlistSymbol]
    
    metadata_changes: Dict[str, Any]
    summary: WatchlistDiffSummary
