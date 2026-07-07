"""
Fresh Watchlist Snapshot ORM Model
==================================

SQLAlchemy mapping for FreshWatchlistSnapshot.
"""
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.mixins import TimestampMixin
from backend.infrastructure.database.orm.watchlist import WatchlistSnapshotModel

class FreshWatchlistSnapshotModel(Base, TimestampMixin):
    """
    SQLAlchemy mapping for FreshWatchlistSnapshot.
    
    Columns:
      - freshness_snapshot_id: Unique UUID (PK).
      - version: Monotonically incremented version.
      - watchlist_snapshot_id: FK to watchlist_snapshots.
      - dataset_version: Canonical dataset version used during validation.
      - parent_candidate_watchlist_version: Lineage pointer to candidate selection.
    """
    __tablename__ = "fresh_watchlist_snapshots"

    freshness_snapshot_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    watchlist_snapshot_id: Mapped[str] = mapped_column(
        String(100), 
        ForeignKey("watchlist_snapshots.snapshot_id"), 
        nullable=False, 
        unique=True
    )
    
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_candidate_watchlist_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationship to the generic WatchlistSnapshotModel
    watchlist_snapshot: Mapped["WatchlistSnapshotModel"] = relationship()
