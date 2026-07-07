"""
Universe Engine Domain Models
=============================

This module defines the core, immutable domain models for the Universe Engine.

IMMUTABILITY CONTRACT
---------------------
UniverseSnapshot is fully immutable. Once created, it must NEVER be modified.

Rules:
  1. A snapshot represents the state of the universe at a specific point in time.
  2. If the universe changes (new data, re-run, updated provider), a NEW snapshot
     must always be created with an incremented version number.
  3. Existing snapshots may never be overwritten, backfilled, or edited.
  4. The repository enforces this via INSERT-only operations — never UPDATE.

EXECUTION LIFECYCLE
-------------------
The standard execution flow for universe generation is:

    IUniverseProvider
         │
         │ fetch_universe() → List[SymbolReference]
         ▼
    UniverseValidator
         │
         │ validate_symbols() → raises UniverseValidationError on failure
         ▼
    UniverseExecutionContext (created with run_id, snapshot_id, provider_name)
         │
         │ passed through each registered IUniverseStage
         ▼
    IUniversePipeline.execute()
         │
         │ produces StageResult per stage
         ▼
    UniverseSnapshot (immutable, frozen, versioned)
         │
         │ saved via IUniverseRepository
         ▼
    UniverseResult (returned to caller)

Notes:
  - If any IUniverseStage returns StageStatus.FAILED, the pipeline halts immediately.
  - If any IUniverseStage raises an unhandled exception, it is wrapped in
    UniversePipelineError and the stage's StageResult is recorded as FAILED.
  - The pipeline_version stored in every snapshot allows future engineers to
    identify exactly which pipeline definition produced each snapshot, making
    debugging significantly easier as the pipeline evolves over time.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Mapping
from datetime import datetime
from enum import Enum

from backend.market_data.models.symbol import SymbolReference


class StageStatus(str, Enum):
    """Represents the outcome of a single pipeline stage execution."""
    SUCCESS = "SUCCESS"  # Stage completed without errors.
    SKIPPED = "SKIPPED"  # Stage was bypassed intentionally (e.g. disabled).
    FAILED = "FAILED"    # Stage encountered a blocking error.


class ValidationStatus(str, Enum):
    """Tracks whether the symbol list passed structural validation."""
    PENDING = "PENDING"  # Validation has not yet been executed.
    PASSED = "PASSED"    # All validation rules passed successfully.
    FAILED = "FAILED"    # One or more validation rules failed.


class InstrumentType(str, Enum):
    """
    Strongly typed instrument type.
    
    EVOLUTION RULES:
    If exchanges introduce new types (e.g. WARRANTS, CRYPTO), add them here.
    Do NOT delete or rename existing types, as this breaks historical snapshots.
    Ensure that config configurations explicitly include/exclude the new type.
    """
    EQUITY = "EQUITY"
    ETF = "ETF"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    BONDS = "BONDS"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"
    MUTUAL_FUND = "MUTUAL_FUND"
    UNKNOWN = "UNKNOWN"


class TradingStatus(str, Enum):
    """
    Strongly typed trading status.
    
    EVOLUTION RULES:
    If exchanges introduce new statuses (e.g. RESTRICTED), add them here.
    Always map unknown or unparseable states from the provider to UNKNOWN,
    and explicitly filter UNKNOWN out if strict safety is desired.
    """
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    HALTED = "HALTED"
    DISABLED = "DISABLED"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"


class MarketSegment(str, Enum):
    """Strongly typed market segment."""
    EQUITY_CASH = "EQUITY_CASH"
    EQUITY_DERIVATIVES = "EQUITY_DERIVATIVES"
    CURRENCY_DERIVATIVES = "CURRENCY_DERIVATIVES"
    COMMODITY_DERIVATIVES = "COMMODITY_DERIVATIVES"
    DEBT = "DEBT"
    UNKNOWN = "UNKNOWN"


class UniverseInstrument(BaseModel):
    """
    Represents an instrument within the Universe Engine.
    
    Contains the core market data reference along with provider-supplied metadata
    required for structural eligibility filtering.
    """
    symbol: SymbolReference
    instrument_type: InstrumentType
    trading_status: TradingStatus
    market_segment: MarketSegment
    is_delisted: bool
    provider_attributes: Mapping[str, Any] = Field(default_factory=dict)


class StageResult(BaseModel):
    """
    Immutable record of a single pipeline stage's execution outcome.

    Stored inside UniverseSnapshot.metadata['stage_results'] to provide
    full observability into what happened during each pipeline run.
    """
    model_config = ConfigDict(frozen=True)

    stage_name: str
    status: StageStatus
    duration_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class UniverseExecutionContext(BaseModel):
    """
    Mutable execution context that is passed through all pipeline stages.

    Stages may:
      - Append to `stage_results` after they complete.
      - Write intermediate data into `shared_state` for downstream stages to read.
      - Append structured execution metadata into `metadata`.
      - Mutate `instruments` by removing ineligible entries.

    The context is NOT frozen because pipeline stages must mutate it progressively.
    After the pipeline completes, an immutable UniverseSnapshot is derived from it.
    """
    run_id: str
    snapshot_id: str
    provider_name: str
    started_at: datetime
    instruments: List[UniverseInstrument]
    shared_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stage_results: List[StageResult] = Field(default_factory=list)


class UniverseSnapshot(BaseModel):
    """
    Immutable, versioned representation of the symbol universe at a point in time.

    IMMUTABILITY RULES (MANDATORY):
    ─────────────────────────────────
    ① Once saved, a UniverseSnapshot must NEVER be modified.
    ② Each pipeline run ALWAYS creates a new snapshot with an incremented `version`.
    ③ The repository uses INSERT-only writes — UPDATE operations on snapshots
       are architecturally prohibited.
    ④ If a bug requires historical correction, a new snapshot must be created
       with corrected data and a higher version number.

    PIPELINE VERSION:
    ─────────────────────────────────
    The `pipeline_version` field records the semantic version of the pipeline
    configuration that produced this snapshot. This is intentionally stored
    on every snapshot (not just in logs) so that future engineers can:
      - Identify snapshots produced under different pipeline configurations.
      - Reproduce historical runs deterministically.
      - Diagnose regressions introduced by pipeline changes.
    """
    model_config = ConfigDict(frozen=True)

    # Unique identifier for this snapshot instance.
    snapshot_id: str

    # Monotonically incremented version number. Every new run produces version + 1.
    version: int

    # Name of the provider that supplied the raw symbol list for this snapshot.
    provider: str

    # UTC timestamp of when this snapshot was created. Used for ordering.
    created_at: datetime

    # Total number of instruments included in this snapshot (derived for convenience).
    symbol_count: int

    # The fully validated list of instruments included in this universe snapshot.
    instruments: List[UniverseInstrument]

    # Structured metadata containing run_id, execution_time_ms, and stage_results.
    metadata: Dict[str, Any]

    # Semantic version of the pipeline that produced this snapshot.
    # Format: "<MAJOR>.<MINOR>.<PATCH>" — e.g. "1.0.0", "1.2.0".
    # Must be incremented in UniverseSettings whenever pipeline stage logic changes.
    pipeline_version: str

    # Whether the instrument list passed structural validation before the pipeline ran.
    validation_status: ValidationStatus


class UniverseResult(BaseModel):
    """
    The top-level result object returned by UniverseEngine.generate_universe().

    Wraps the immutable UniverseSnapshot produced by a single pipeline run.
    """
    model_config = ConfigDict(frozen=True)

    snapshot: UniverseSnapshot
