"""
Watchlist Snapshot ORM Model
=============================

SQLAlchemy mapping for WatchlistSnapshot.
Persists immutable, versioned watchlist snapshots.

IMMUTABILITY ENFORCEMENT:
The repository uses INSERT-only operations.
UPDATE operations on this table are architecturally prohibited.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.mixins import TimestampMixin
from sqlalchemy import JSON


class WatchlistSnapshotModel(Base, TimestampMixin):
    """
    SQLAlchemy mapping for WatchlistSnapshot.

    Columns:
      - snapshot_id: Unique UUID for the snapshot (primary key).
      - version: Monotonically incremented version number.
      - created_at: Provided by TimestampMixin.
      - updated_at: Provided by TimestampMixin.
      - symbol_count: Total number of candidates in this snapshot.
      - candidates: JSON-serialized list of WatchlistCandidate objects.
      - metadata_col: JSON execution metadata (run_id, stage_results, stats).
      - pipeline_version: Semantic version of the watchlist pipeline.
      - validation_status: Whether structural validation passed.
      - source_pipeline_version: Upstream universe pipeline version for lineage.
    """
    __tablename__ = "watchlist_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # created_at and updated_at are provided by TimestampMixin.

    symbol_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # JSON-serialized WatchlistCandidate list.
    candidates: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)

    # Execution metadata: run_id, stage_results, pipeline_statistics, etc.
    metadata_col: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, nullable=False)

    # Semantic version of the watchlist pipeline configuration.
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    candidate_selection_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Hash of the configuration used to generate this watchlist.
    config_hash: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")

    # Structural validation outcome.
    validation_status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Traces the upstream Universe Engine pipeline version for full lineage.
    source_pipeline_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Traces the upstream universe snapshot ID for lineage tracking.
    source_universe_snapshot_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Traces the upstream universe snapshot version for lineage tracking.
    source_universe_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
