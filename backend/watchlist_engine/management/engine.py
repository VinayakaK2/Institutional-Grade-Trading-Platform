import datetime
import hashlib
import uuid
import json

from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistAuditRecord, WatchlistStatus
from backend.watchlist_engine.management.contracts import IWatchlistManagementEngine, IManagedWatchlistRepository
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot

class WatchlistManagementEngine(IWatchlistManagementEngine):
    """
    Manages the elevation of a FreshWatchlistSnapshot to a fully managed and verified ManagedWatchlistSnapshot.
    """
    def __init__(self, repository: IManagedWatchlistRepository):
        self._repository = repository

    async def generate_managed_watchlist(self, fresh_snapshot: FreshWatchlistSnapshot) -> ManagedWatchlistSnapshot:
        """
        Validates lineage, computes business fingerprint, and generates a ManagedWatchlistSnapshot.
        Stores the snapshot and audit record atomically.
        """
        # Load latest to determine monotonic versioning
        latest = await self._repository.load_latest_managed_snapshot()
        new_version = latest.version + 1 if latest else 1

        # Extract lineage
        base_snapshot = fresh_snapshot.watchlist_snapshot
        
        # We must enforce that the parent universe exists and the config hash exists
        if base_snapshot.source_universe_version is None:
            raise ValueError("Invalid Lineage: source_universe_version is missing")
        if not base_snapshot.config_hash:
            raise ValueError("Invalid Lineage: config_hash is missing")
            
        dataset_version = fresh_snapshot.dataset_version
        
        # Calculate Deterministic Business Fingerprint
        # - Symbol IDs
        # - Dataset Version
        # - Configuration Hash
        symbol_ids = sorted([f"{c.watchlist_symbol.symbol.symbol}:{c.watchlist_symbol.symbol.exchange.code}" for c in base_snapshot.candidates])
        fingerprint_data = {
            "symbols": symbol_ids,
            "dataset_version": dataset_version,
            "config_hash": base_snapshot.config_hash
        }
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        business_fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()
        
        now = datetime.datetime.now(datetime.timezone.utc)
        managed_snapshot_id = str(uuid.uuid4())
        
        managed_snapshot = ManagedWatchlistSnapshot(
            managed_snapshot_id=managed_snapshot_id,
            version=new_version,
            fresh_watchlist_snapshot=fresh_snapshot,
            parent_fresh_watchlist_version=fresh_snapshot.version,
            parent_candidate_watchlist_version=str(base_snapshot.version), # Or fresh_snapshot.parent_candidate_watchlist_version depending on structure, let's use base_snapshot.version since it is the candidate watchlist version. Wait, actually FreshWatchlistSnapshot HAS parent_candidate_watchlist_version. Let's use it.
            parent_universe_version=base_snapshot.source_universe_version,
            dataset_version=dataset_version,
            pipeline_version=base_snapshot.pipeline_version,
            config_hash=base_snapshot.config_hash,
            business_fingerprint=business_fingerprint,
            created_at=now,
            status=WatchlistStatus.VALID
        )
        
        # Correct the parent candidate watchlist version using the explicitly tracked one in fresh_snapshot
        managed_snapshot = managed_snapshot.model_copy(update={
            "parent_candidate_watchlist_version": fresh_snapshot.parent_candidate_watchlist_version
        })
        
        audit_record = WatchlistAuditRecord(
            event_id=str(uuid.uuid4()),
            managed_snapshot_id=managed_snapshot_id,
            event_type="SNAPSHOT_CREATED",
            timestamp=now,
            metadata={
                "version": new_version,
                "parent_fresh_watchlist_version": fresh_snapshot.version,
                "parent_candidate_watchlist_version": fresh_snapshot.parent_candidate_watchlist_version,
                "business_fingerprint": business_fingerprint
            }
        )
        
        await self._repository.save_managed_snapshot(managed_snapshot, audit_record)
        return managed_snapshot
