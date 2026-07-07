# Watchlist Foundation Architecture
## Phase 6.1 — Reference Document

This document is the authoritative architectural reference for the Watchlist Engine.
Every future Watchlist phase (6.2+) must comply with the contracts and lifecycle defined here.

---

## 1. Scope & Boundaries

The Watchlist Foundation is responsible **only** for:

- Providing a reusable pipeline and engine lifecycle.
- Persisting immutable, versioned watchlist snapshots.
- Validating structural integrity of candidate inputs.

It is **explicitly NOT responsible** for:

| Concern | Belongs To |
|---|---|
| Candidate selection | Phase 6.2+ |
| EMA / trend filtering | Phase 6.3+ |
| Relative strength ranking | Phase 6.4+ |
| Risk management | Later phases |
| Trade signals / Buy-Sell decisions | Later phases |

---

## 2. Boundary Model — WatchlistSymbol

### Why WatchlistSymbol exists

The Watchlist Engine must not depend on `UniverseInstrument` (from the Universe Engine).
Doing so would create a tight coupling across module boundaries.

Instead, **WatchlistSymbol** is a dedicated boundary model that carries enough information
for the Watchlist layer without importing Universe Engine internals.

```
UniverseEngine (Phase 5)
      │
      │  Produces ClassifiedUniverse / OptimizedUniverse
      ▼
 [BOUNDARY]
      │
      │  Caller converts ClassifiedSymbol → WatchlistSymbol
      ▼
WatchlistEngine (Phase 6)
```

### WatchlistSymbol fields

| Field | Type | Description |
|---|---|---|
| `symbol` | `SymbolReference` | Ticker + exchange identity. |
| `market_segment` | `str` | E.g., `EQUITY_CASH`. |
| `instrument_type` | `str` | E.g., `EQUITY`, `ETF`. |
| `provider_metadata` | `Mapping[str, Any]` | Optional provider-specific metadata. |

Future phases may add fields to `WatchlistSymbol` without breaking the contract.

---

## 3. Engine Lifecycle

```
generate_watchlist(run_id, candidates: List[WatchlistCandidate])
         │
         │  1. IWatchlistValidator.validate(candidates)
         │     └─ Raises WatchlistValidationError on failure
         │     └─ validation_status = PASSED
         ▼
WatchlistExecutionContext(run_id, snapshot_id, candidates, …)
         │
         │  2. IWatchlistPipeline.execute(context)
         │     └─ Executes stages in registration order
         │     └─ Halts on first FAILED stage
         │     └─ Wraps unhandled exceptions in WatchlistPipelineError
         ▼
context (mutated — stage_results appended)
         │
         │  3. IWatchlistRepository.load_latest_snapshot()
         │     └─ Determines next version number (latest.version + 1, or 1 if none)
         ▼
WatchlistSnapshot (frozen, versioned, pipeline_version stamped)
         │
         │  4. IWatchlistRepository.save_snapshot(snapshot)
         │     └─ INSERT-only — never UPDATE
         ▼
WatchlistResult(snapshot=snapshot)
```

### Statelessness Guarantee

The engine is **stateless**. It retains no candidate data between runs.
The same `WatchlistEngine` instance can safely serve multiple concurrent, independent runs.

---

## 4. Snapshot Lifecycle & Immutability Contract

```
Run 1:  WatchlistSnapshot(version=1, snapshot_id="uuid-a", …)  ← CREATED, FROZEN
Run 2:  WatchlistSnapshot(version=2, snapshot_id="uuid-b", …)  ← NEW, FROZEN
Run 3:  WatchlistSnapshot(version=3, snapshot_id="uuid-c", …)  ← NEW, FROZEN
```

### Rules (MANDATORY)

1. **INSERT-only**: Once a snapshot is written to the repository, it must **never** be updated or overwritten.
2. **Monotonic versions**: Each run produces `previous_version + 1`. Versions never decrease.
3. **Immutable Pydantic model**: `WatchlistSnapshot` is a `ConfigDict(frozen=True)` Pydantic model.
4. **Historical correction**: If a snapshot contains an error, a **new** snapshot with corrected data and a higher version must be created.
5. **Pipeline version stamping**: Every snapshot records the semantic version of the pipeline that produced it.

### When to increment `pipeline_version`

| Change | Increment |
|---|---|
| Bug fix in an existing stage (no logic change) | PATCH (1.0.0 → 1.0.1) |
| New optional stage added | MINOR (1.0.0 → 1.1.0) |
| Stage removed or filtering contract changed | MAJOR (1.0.0 → 2.0.0) |

---

## 5. Pipeline Lifecycle

```
WatchlistExecutionPipeline
         │
         │  register_stage(IWatchlistStage)  ← raises if max_stages exceeded
         │
         │  execute(WatchlistExecutionContext)
         │     │
         │     ├─ For each stage (in registration order):
         │     │     ├─ stage.execute(context) → WatchlistStageResult
         │     │     ├─ context.stage_results.append(result)
         │     │     ├─ If FAILED → halt
         │     │     └─ If exception → record FAILED result → raise WatchlistPipelineError
         │     │
         │     └─ Return mutated context
```

### Context Mutation Rules

The `WatchlistExecutionContext` is intentionally mutable so stages can accumulate data.

**Allowed mutations:**
- Append to `context.stage_results`.
- Write to `context.shared_state`.
- Write to `context.metadata`.
- Write to `candidate.stage_metadata`.
- Remove candidates from `context.candidates` (future filtering stages).

**Prohibited mutations:**
- Mutate `WatchlistCandidate.watchlist_symbol` (the symbol identity is immutable).
- Mutate `WatchlistStageResult` after appending (it is frozen).
- Mutate `WatchlistSnapshot` (it is frozen).

---

## 6. Validation Contract

`IWatchlistValidator` enforces **structural integrity only** — no business rules.

| Rule | Behaviour |
|---|---|
| Empty list (`allow_empty_watchlist=False`) | Raises `WatchlistValidationError` |
| Candidate list exceeds `max_watchlist_size` | Raises `WatchlistValidationError` |
| `None` candidate entry | Raises `WatchlistValidationError` |
| `None` `WatchlistSymbol` | Raises `WatchlistValidationError` |
| `None` `SymbolReference` | Raises `WatchlistValidationError` |
| Empty or whitespace ticker | Raises `WatchlistValidationError` |
| Duplicate `symbol.full_name` in same list | Raises `WatchlistValidationError` |

**Never validates:** liquidity, trend, ranking, trading rules, session validity.

---

## 7. Repository Design

### Implementations

| Implementation | Usage |
|---|---|
| `InMemoryWatchlistRepository` | Testing, local development. No external dependencies. |
| `PostgreSQLWatchlistRepository` | Production. Async SQLAlchemy. INSERT-only. |

### Available operations

| Method | Description |
|---|---|
| `save_snapshot(snapshot)` | INSERT-only. Never UPDATE. |
| `load_snapshot(snapshot_id)` | Load by unique ID. Returns `None` if not found. |
| `load_latest_snapshot()` | Load snapshot with the highest version number. |
| `load_snapshot_by_version(version)` | Load snapshot by exact version. Returns `None` if not found. |
| `list_snapshot_history(limit)` | Return last N snapshots, ordered by version descending. |

### Ordering Note

`load_latest_snapshot()` uses **version** (monotonic) rather than `created_at` (clock-dependent)
for ordering. This prevents incorrect behavior when multiple runs execute within the same
clock tick (a common occurrence in fast test environments).

### Snapshot Version Semantics (Explicit Contract)

These rules govern snapshot versions and must never be inferred by future contributors.

| Rule | Detail |
|---|---|
| **Monotonically increasing** | Each successful `generate_watchlist()` call produces `previous_version + 1`. Versions never decrease. |
| **Versions are never reused** | Once a version number has been assigned to any snapshot, that version number is permanently retired — even if the snapshot is later logically deleted or superseded. |
| **Deletion does not reclaim version numbers** | If snapshot v5 is removed for any operational reason, the next run still produces v6. Version gaps are permitted and must not be treated as errors. |
| **Version is the ordering key** | All queries that need "most recent" must order by `version DESC`, not by `created_at`. Timestamps are not reliable ordering keys under high concurrency or fast test execution. |
| **First run always produces version 1** | When the repository contains no prior snapshots, the first run always produces version 1. There is no version 0. |

### Repository Consistency Guarantees (Atomicity Contract)

Repository write operations are **atomic**. A snapshot is either:

- **Completely persisted** — all fields written in a single transaction, and the row is visible to subsequent reads.
- **Not persisted at all** — if the write fails for any reason, no partial row is left behind.

Partial persistence (a snapshot row with missing columns or incomplete JSON) must **never** occur.

This is guaranteed by the underlying database transaction. Both implementations enforce this:

| Implementation | Mechanism |
|---|---|
| `InMemoryWatchlistRepository` | Dict assignment is atomic in CPython — the snapshot is either in the dict or not. |
| `PostgreSQLWatchlistRepository` | Uses `async with session.begin()` — the transaction commits only if all writes succeed; any failure triggers a full rollback. |

> **For future contributors:** Do not remove `session.begin()` from PostgreSQL write paths. It is not optional — it is the atomicity boundary.

---

## 8. Dependency Graph

```
WatchlistEngine
      │
      ├── IWatchlistPipeline ──────────────── WatchlistExecutionPipeline
      │         │
      │         └── IWatchlistStage (registered externally)
      │
      ├── IWatchlistRepository ────────────── InMemoryWatchlistRepository
      │                                       PostgreSQLWatchlistRepository
      │
      ├── IWatchlistValidator ─────────────── WatchlistValidator
      │
      └── WatchlistSettings
                │
                ├── WatchlistPipelineSettings
                ├── WatchlistValidationSettings
                ├── WatchlistRepositorySettings
                └── WatchlistSnapshotSettings

WatchlistSymbol (boundary model)
      │
      └── SymbolReference (shared kernel — market_data.models.symbol)

Phase 0 Foundation (shared by all modules)
      │
      ├── PlatformException
      ├── AppSettings
      └── structlog Logger
```

---

## 9. Architectural Boundaries

### What future phases (6.2+) may do

- Register new `IWatchlistStage` implementations into the pipeline.
- Extend `WatchlistSymbol` with additional fields (additive, non-breaking).
- Add new validation rules by composing or extending `WatchlistValidator`.
- Read snapshots via `IWatchlistRepository.load_snapshot()` for analysis.

### What future phases must NOT do

- Modify `WatchlistEngine`, `WatchlistExecutionPipeline`, or `WatchlistValidator` to embed business logic.
- Add candidate selection, scoring, or ranking inside this module.
- Write UPDATE operations against the `watchlist_snapshots` table.
- Remove existing fields from `WatchlistSymbol` or `WatchlistSnapshot` (backward-incompatible).
- Create a direct dependency from `watchlist_engine` to `universe_engine` internals.

---

## 10. Exception Hierarchy

```
PlatformException (Phase 0)
      │
      ├── WatchlistConfigurationError  (WATCHLIST_CONFIG_ERROR, 500)
      ├── WatchlistPipelineError       (WATCHLIST_PIPELINE_ERROR, 500)
      ├── WatchlistValidationError     (WATCHLIST_VALIDATION_ERROR, 400)
      ├── WatchlistRepositoryError     (WATCHLIST_REPOSITORY_ERROR, 500)
      └── WatchlistSnapshotError       (WATCHLIST_SNAPSHOT_ERROR, 500)
```

---

## 11. Database Schema

### Table: `watchlist_snapshots`

| Column | Type | Notes |
|---|---|---|
| `snapshot_id` | `VARCHAR(100)` | Primary Key (UUID). |
| `version` | `INTEGER` | Monotonic. Indexed. |
| `created_at` | `DATETIME(tz)` | Write timestamp. |
| `updated_at` | `DATETIME(tz)` | Always equals `created_at` — never updated. |
| `symbol_count` | `INTEGER` | Pre-computed. |
| `candidates` | `JSON` | Serialized `WatchlistCandidate` list. |
| `metadata` | `JSON` | `run_id`, `stage_results`, `pipeline_statistics`. |
| `pipeline_version` | `VARCHAR(50)` | Watchlist pipeline version. |
| `validation_status` | `VARCHAR(50)` | `PASSED` / `FAILED`. |
| `source_pipeline_version` | `VARCHAR(50)` | Nullable. Upstream Universe pipeline version. |

**Alembic revision:** `d1e9f2a3b4c5`

---

*This document must be updated whenever the Watchlist Foundation contracts change.*
*All future Watchlist phases must reference this document before implementation.*
