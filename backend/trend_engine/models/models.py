"""
Trend Engine Domain Models
==========================

Core, immutable domain models for the Trend Engine.

IMMUTABILITY CONTRACT
---------------------
TrendSnapshot is fully immutable. Once created, it must NEVER be modified.

Rules:
  1. A snapshot represents the state of the trends at a specific point in time.
  2. If the trend computation changes (new data, re-run), a NEW snapshot
     must always be created with an incremented version number.
  3. Existing snapshots may never be overwritten, backfilled, or edited.
  4. The repository enforces this via INSERT-only operations — never UPDATE.
"""
import hashlib
import json
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

from backend.watchlist_engine.models.models import WatchlistSymbol


class TrendDirection(str, Enum):
    """Direction of the detected trend."""
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


class TrendState(str, Enum):
    """Structural state of the detected trend."""
    VALID = "VALID"
    INVALID = "INVALID"
    INCOMPLETE = "INCOMPLETE"


class TrendStageStatus(str, Enum):
    """Represents the outcome of a single trend pipeline stage execution."""
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class TrendSymbol(BaseModel):
    """
    Dedicated boundary model for the Trend Engine.

    Consumes existing immutable Watchlist symbols directly.
    Future phases can enrich this model with trend direction, strength, etc., 
    without affecting Watchlist contracts.
    
    Fields:
      - watchlist_symbol: The underlying Watchlist symbol.
      - direction: Detected trend direction.
      - state: Detected trend structural state.
      - stage_metadata: Metadata accumulated across structural pipeline stages.
    """
    watchlist_symbol: WatchlistSymbol
    direction: TrendDirection = TrendDirection.UNKNOWN
    state: TrendState = TrendState.INCOMPLETE
    stage_metadata: Dict[str, Any] = Field(default_factory=dict)


class TrendStageResult(BaseModel):
    """
    Immutable record of a single pipeline stage's execution outcome.

    Stored inside TrendSnapshot.metadata['stage_results'] to provide
    full observability into what happened during each pipeline run.
    """
    model_config = ConfigDict(frozen=True)

    stage_name: str
    status: TrendStageStatus
    duration_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class TrendSnapshot(BaseModel):
    """
    Immutable, versioned representation of the trend foundation at a point in time.

    IMMUTABILITY RULES:
    ─────────────────────────────────
    ① Once saved, a TrendSnapshot must NEVER be modified.
    ② Each pipeline run ALWAYS creates a new snapshot with an incremented `version`.
    ③ The repository uses INSERT-only writes.
    """
    model_config = ConfigDict(frozen=True)

    # Unique identifier for this snapshot instance.
    snapshot_id: str

    # Monotonically incremented version number. Every new run produces version + 1.
    snapshot_version: int

    # Lineage tracking
    source_watchlist_snapshot_id: str
    source_watchlist_version: int
    
    source_indicator_snapshot_id: str
    source_indicator_snapshot_version: int
    
    source_structure_snapshot_id: str
    source_structure_snapshot_version: int

    # UTC timestamp of when this snapshot was created.
    created_at: datetime

    # The symbols included in this trend snapshot.
    symbols: List[TrendSymbol]
    
    # Semantic version of the trend pipeline that produced this snapshot.
    pipeline_version: str

    # Hash of the configuration used to generate this trend snapshot.
    configuration_hash: str
    
    # Schema version for configuration compatibility.
    schema_version: str

    # Execution metadata (e.g. run_id, memory usage)
    execution_metadata: Dict[str, Any]

    # Audit metadata (e.g. stage_results)
    audit_metadata: Dict[str, Any]

    def generate_business_fingerprint(self) -> str:
        """
        Generates a deterministic Business Fingerprint for the snapshot.
        
        This fingerprint includes ONLY business-impacting information:
        - source_watchlist_version
        - source_indicator_snapshot_version
        - source_structure_snapshot_version
        - configuration_hash
        - pipeline_version
        - schema_version
        - ordered symbol identifiers with direction and state
        
        It excludes timestamps, execution duration, audit IDs, debug metadata,
        and runtime metadata. Future optimization depends on this.
        """
        symbol_ids = sorted([
            f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}:{ts.direction.name}:{ts.state.name}" 
            for ts in self.symbols
        ])
        
        fingerprint_data = {
            "source_watchlist_version": self.source_watchlist_version,
            "source_indicator_snapshot_version": self.source_indicator_snapshot_version,
            "source_structure_snapshot_version": self.source_structure_snapshot_version,
            "configuration_hash": self.configuration_hash,
            "pipeline_version": self.pipeline_version,
            "schema_version": self.schema_version,
            "symbols": symbol_ids
        }
        
        # Serialize deterministically
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()
