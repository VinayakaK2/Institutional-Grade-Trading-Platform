"""create_watchlist_snapshots_table

Revision ID: d1e9f2a3b4c5
Revises: 8bb4c5ddd99b
Create Date: 2026-07-07

Creates the watchlist_snapshots table for the Watchlist Engine (Phase 6.1).

TABLE: watchlist_snapshots
  - snapshot_id: Primary key (UUID string).
  - version: Monotonic version number, indexed for fast version lookups.
  - created_at / updated_at: Timestamps provided by TimestampMixin convention.
  - symbol_count: Pre-computed candidate count.
  - candidates: JSON-serialized WatchlistCandidate list.
  - metadata: JSON execution metadata (run_id, stage_results, pipeline_statistics).
  - pipeline_version: Semantic version of the watchlist pipeline.
  - validation_status: Structural validation outcome.
  - source_pipeline_version: Upstream Universe Engine pipeline version for lineage.

IMMUTABILITY NOTE:
  This table is INSERT-only. No UPDATE operations are permitted on existing rows.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection


# Revision identifiers, used by Alembic.
revision: str = "d1e9f2a3b4c5"
down_revision: Union[str, None] = "8bb4c5ddd99b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Check whether a table already exists in the current database."""
    bind = op.get_bind()
    inspector = reflection.Inspector.from_engine(bind)  # type: ignore[arg-type]
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Creates the watchlist_snapshots table (idempotent — skips if already exists)."""
    # Guard: the table may already exist if a previous failed migration run created it.
    if _table_exists("watchlist_snapshots"):
        return

    op.create_table(
        "watchlist_snapshots",
        sa.Column("snapshot_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="When the record was created",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="When the record was last updated",
        ),
        sa.Column("symbol_count", sa.Integer(), nullable=False),
        sa.Column("candidates", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("pipeline_version", sa.String(length=50), nullable=False),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("source_pipeline_version", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("snapshot_id", name=op.f("pk_watchlist_snapshots")),
    )
    op.create_index(
        op.f("ix_watchlist_snapshots_snapshot_id"),
        "watchlist_snapshots",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watchlist_snapshots_version"),
        "watchlist_snapshots",
        ["version"],
        unique=False,
    )


def downgrade() -> None:
    """Drops the watchlist_snapshots table and all associated indexes."""
    if not _table_exists("watchlist_snapshots"):
        return
    op.drop_index(op.f("ix_watchlist_snapshots_version"), table_name="watchlist_snapshots")
    op.drop_index(op.f("ix_watchlist_snapshots_snapshot_id"), table_name="watchlist_snapshots")
    op.drop_table("watchlist_snapshots")
