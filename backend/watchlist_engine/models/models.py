"""
Watchlist Engine Domain Models
==============================

Core, immutable domain models for the Watchlist Engine.

IMMUTABILITY CONTRACT
---------------------
WatchlistSnapshot is fully immutable. Once created, it must NEVER be modified.

Rules:
  1. A snapshot represents the state of the watchlist at a specific point in time.
  2. If the watchlist changes (new data, re-run), a NEW snapshot
     must always be created with an incremented version number.
  3. Existing snapshots may never be overwritten, backfilled, or edited.
  4. The repository enforces this via INSERT-only operations — never UPDATE.

BOUNDARY MODEL
--------------
WatchlistSymbol is a dedicated boundary model that isolates the Watchlist
Engine from the Universe Engine's internal models. It carries enough
instrument identity and metadata for the watchlist layer without creating
a direct dependency on UniverseInstrument.

EXECUTION LIFECYCLE
-------------------
    Caller provides List[WatchlistCandidate]
         │
         │ validate(candidates) → raises WatchlistValidationError on failure
         ▼
    WatchlistExecutionContext (created with run_id, snapshot_id)
         │
         │ passed through each registered IWatchlistStage
         ▼
    IWatchlistPipeline.execute()
         │
         │ produces WatchlistStageResult per stage
         ▼
    WatchlistSnapshot (immutable, frozen, versioned)
         │
         │ saved via IWatchlistRepository
         ▼
    WatchlistResult (returned to caller)
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Mapping, Optional
from datetime import datetime
from enum import Enum

from backend.market_data.models.symbol import SymbolReference


class WatchlistStageStatus(str, Enum):
    """Represents the outcome of a single watchlist pipeline stage execution."""
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class WatchlistValidationStatus(str, Enum):
    """Tracks whether the candidate list passed structural validation."""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class WatchlistSymbol(BaseModel):
    """
    Dedicated boundary model for the Watchlist Engine.

    Carries essential instrument identity and metadata without depending
    on the Universe Engine's internal models (UniverseInstrument).
    Future phases can enrich this model without affecting Universe contracts.

    Fields:
      - symbol: Core symbol identity (ticker + exchange).
      - market_segment: The segment this instrument belongs to.
      - instrument_type: Classification of the instrument (EQUITY, ETF, etc.).
      - provider_metadata: Optional provider-specific attributes carried forward.
    """
    symbol: SymbolReference
    market_segment: str = "UNKNOWN"
    instrument_type: str = "UNKNOWN"
    provider_metadata: Mapping[str, Any] = Field(default_factory=dict)


class WatchlistCandidate(BaseModel):
    """
    A candidate symbol being processed through the Watchlist pipeline.

    Wraps the boundary model WatchlistSymbol with stage-contributed metadata
    that accumulates as the candidate passes through pipeline stages.

    The candidate itself is not frozen — stages may write to stage_metadata.
    However, the underlying WatchlistSymbol identity must not be mutated.
    """
    watchlist_symbol: WatchlistSymbol
    stage_metadata: Dict[str, Any] = Field(default_factory=dict)


class WatchlistStageResult(BaseModel):
    """
    Immutable record of a single pipeline stage's execution outcome.

    Stored inside WatchlistSnapshot.metadata['stage_results'] to provide
    full observability into what happened during each pipeline run.
    """
    model_config = ConfigDict(frozen=True)

    stage_name: str
    status: WatchlistStageStatus
    duration_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class WatchlistExecutionContext(BaseModel):
    """
    Mutable execution context that is passed through all pipeline stages.

    Stages may:
      - Append to `stage_results` after they complete.
      - Write intermediate data into `shared_state` for downstream stages.
      - Append structured execution metadata into `metadata`.
      - Read from `candidates` but must NOT mutate WatchlistSymbol identity.

    The context is NOT frozen because pipeline stages must accumulate results.
    After the pipeline completes, an immutable WatchlistSnapshot is derived from it.

    MUTATION RULES:
      - `candidates` list membership may change (stages can filter out candidates).
      - `WatchlistCandidate.stage_metadata` may be written to.
      - `WatchlistCandidate.watchlist_symbol` MUST NEVER be mutated.
    """
    run_id: str
    snapshot_id: str
    started_at: datetime
    candidates: List[WatchlistCandidate]
    shared_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stage_results: List[WatchlistStageResult] = Field(default_factory=list)


class WatchlistSnapshot(BaseModel):
    """
    Immutable, versioned representation of the watchlist at a point in time.

    IMMUTABILITY RULES (MANDATORY):
    ─────────────────────────────────
    ① Once saved, a WatchlistSnapshot must NEVER be modified.
    ② Each pipeline run ALWAYS creates a new snapshot with an incremented `version`.
    ③ The repository uses INSERT-only writes — UPDATE operations on snapshots
       are architecturally prohibited.
    ④ If a bug requires historical correction, a new snapshot must be created
       with corrected data and a higher version number.

    PIPELINE VERSION:
    ─────────────────────────────────
    The `pipeline_version` field records the semantic version of the watchlist
    pipeline configuration that produced this snapshot.
    """
    model_config = ConfigDict(frozen=True)

    # Unique identifier for this snapshot instance.
    snapshot_id: str

    # Monotonically incremented version number. Every new run produces version + 1.
    version: int

    # UTC timestamp of when this snapshot was created.
    created_at: datetime

    # Total number of candidates included in this snapshot.
    symbol_count: int

    # The candidates included in this watchlist snapshot.
    candidates: List[WatchlistCandidate]

    # Structured metadata containing run_id, execution_time_ms, and stage_results.
    metadata: Dict[str, Any]

    # Semantic version of the watchlist pipeline that produced this snapshot.
    pipeline_version: str

    # Version of the candidate selection engine that generated the candidates.
    candidate_selection_version: Optional[str] = None

    # Hash of the configuration used to generate this watchlist.
    config_hash: str

    # Whether the candidate list passed structural validation before the pipeline ran.
    validation_status: WatchlistValidationStatus

    # Traces the upstream pipeline version that generated the universe.
    source_pipeline_version: Optional[str] = None

    # Traces the upstream universe snapshot ID for lineage tracking.
    source_universe_snapshot_id: Optional[str] = None

    # Traces the upstream universe snapshot version for lineage tracking.
    source_universe_version: Optional[int] = None


class WatchlistResult(BaseModel):
    """
    The top-level result object returned by WatchlistEngine.generate_watchlist().

    Wraps the immutable WatchlistSnapshot produced by a single pipeline run.
    """
    model_config = ConfigDict(frozen=True)

    snapshot: WatchlistSnapshot
