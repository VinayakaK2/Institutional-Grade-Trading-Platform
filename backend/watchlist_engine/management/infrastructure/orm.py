import datetime
from typing import Dict, Any

from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.orm.base import Base

class ManagedWatchlistSnapshotModel(Base):
    __tablename__ = "managed_watchlist_snapshots"

    managed_snapshot_id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    
    # We only store the ID to the FreshWatchlistSnapshot rather than embedding it, 
    # to avoid deep nesting in the ORM. The repository will join it.
    fresh_snapshot_id: Mapped[str] = mapped_column(String, ForeignKey("fresh_watchlist_snapshots.freshness_snapshot_id"), unique=True)
    
    parent_fresh_watchlist_version: Mapped[int] = mapped_column(Integer)
    parent_candidate_watchlist_version: Mapped[str] = mapped_column(String)
    parent_universe_version: Mapped[int] = mapped_column(Integer)
    dataset_version: Mapped[str] = mapped_column(String)
    pipeline_version: Mapped[str] = mapped_column(String)
    config_hash: Mapped[str] = mapped_column(String)
    
    business_fingerprint: Mapped[str] = mapped_column(String, index=True)
    
    status: Mapped[str] = mapped_column(String)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

class WatchlistAuditRecordModel(Base):
    __tablename__ = "managed_watchlist_audit_records"
    
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    managed_snapshot_id: Mapped[str] = mapped_column(String, ForeignKey("managed_watchlist_snapshots.managed_snapshot_id"), index=True)
    
    event_type: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    
    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
