import pytest
import asyncio
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.trend_engine.models.models import (
    TrendSymbol, TrendStageResult, TrendSnapshot, TrendStageStatus
)
from backend.trend_engine.config.config import TrendSettings, TrendPipelineSettings
from backend.trend_engine.validation.validator import TrendValidator, TrendValidationError
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.trend_engine.pipeline.pipeline import TrendPipeline, TrendPipelineError
from backend.trend_engine.pipeline.snapshot_builder import SnapshotBuilder
from backend.trend_engine.repository.memory import InMemoryTrendRepository
from backend.trend_engine.engine.engine import TrendEngine
from backend.trend_engine.contracts.contracts import ITrendStage
from backend.trend_engine.exceptions import (
    DuplicateSnapshotVersionError,
    TrendRepositoryError,
    MissingIndicatorDataError,
    MissingStructureDataError,
    InvalidConfigurationError,
    InvalidSnapshotLineageError,
    TrendPipelineExecutionError
)

# --- Fixtures ---

@pytest.fixture
def sample_watchlist_symbol():
    return WatchlistSymbol(
        symbol=SymbolReference(
            symbol="AAPL",
            exchange=ExchangeReference(code="NASDAQ", name="NASDAQ", country="US")
        ),
        market_segment="US_EQUITY",
        instrument_type="COMMON_STOCK",
        provider_metadata={}
    )

@pytest.fixture
def sample_trend_symbols(sample_watchlist_symbol):
    return [TrendSymbol(watchlist_symbol=sample_watchlist_symbol)]

@pytest.fixture
def trend_settings():
    return TrendSettings()

@pytest.fixture
def snapshot_builder():
    return SnapshotBuilder()

# --- 1. Models & Fingerprint Tests ---

def test_trend_snapshot_immutability(sample_trend_symbols):
    snapshot = TrendSnapshot(
        snapshot_id="test_id",
        snapshot_version=1,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        created_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        pipeline_version="1.0.0",
        configuration_hash="hash1",
        schema_version="1.0.0",
        execution_metadata={},
        audit_metadata={}
    )
    with pytest.raises(ValidationError):
        snapshot.snapshot_version = 2

def test_business_fingerprint_stability(sample_trend_symbols):
    snapshot1 = TrendSnapshot(
        snapshot_id="id_1",
        snapshot_version=1,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        created_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        pipeline_version="1.0.0",
        configuration_hash="hash_x",
        schema_version="1.0.0",
        execution_metadata={"duration": 100},
        audit_metadata={"auditor": "a"}
    )
    
    snapshot2 = TrendSnapshot(
        snapshot_id="id_2",  # Different
        snapshot_version=2,  # Different
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        created_at=datetime.now(timezone.utc),  # Different
        symbols=sample_trend_symbols,
        pipeline_version="1.0.0",
        configuration_hash="hash_x",
        schema_version="1.0.0",
        execution_metadata={"duration": 999},  # Different
        audit_metadata={"auditor": "b"}  # Different
    )
    
    # Fingerprints should match exactly because business fields match
    assert snapshot1.generate_business_fingerprint() == snapshot2.generate_business_fingerprint()

# --- 2. Configuration Hash Stability ---

def test_config_hash_stability():
    config1 = TrendSettings(
        schema_version="1.0.0",
        pipeline=TrendPipelineSettings(fail_fast=True)
    )
    config2 = TrendSettings(
        schema_version="1.0.0",
        pipeline=TrendPipelineSettings(fail_fast=True)
    )
    assert config1.generate_hash() == config2.generate_hash()
    
    config3 = TrendSettings(
        schema_version="1.0.0",
        pipeline=TrendPipelineSettings(fail_fast=False)
    )
    assert config1.generate_hash() != config3.generate_hash()

# --- 3. Validation Tests ---

def test_validator_empty_input():
    validator = TrendValidator()
    with pytest.raises(TrendValidationError, match="cannot be empty"):
        validator.validate_input([])

def test_validator_duplicate_symbols(sample_trend_symbols):
    validator = TrendValidator()
    dup_symbols = sample_trend_symbols + sample_trend_symbols
    with pytest.raises(TrendValidationError, match="Duplicate symbol"):
        validator.validate_input(dup_symbols)

def test_validator_null_symbols(sample_trend_symbols):
    validator = TrendValidator()
    with pytest.raises(TrendValidationError, match="Null symbol"):
        validator.validate_input(sample_trend_symbols + [None])

def test_validator_snapshot_version_duplicate(sample_trend_symbols):
    validator = TrendValidator()
    snapshot = TrendSnapshot(
        snapshot_id="id_1",
        snapshot_version=1,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        created_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        pipeline_version="1.0.0",
        configuration_hash="hash_x",
        schema_version="1.0.0",
        execution_metadata={},
        audit_metadata={}
    )
    with pytest.raises(TrendValidationError, match="Duplicate or invalid snapshot version"):
        validator.validate_snapshot(snapshot, previous_snapshot=snapshot)

# --- 4. Pipeline & Context Tests ---

class MockStage(ITrendStage):
    def __init__(self, name: str, should_fail: bool = False):
        self._name = name
        self.should_fail = should_fail
        
    @property
    def name(self) -> str:
        return self._name

    async def execute(self, context: TrendExecutionContext) -> TrendStageResult:
        if self.should_fail:
            return TrendStageResult(
                stage_name=self.name, status=TrendStageStatus.FAILED, duration_ms=10.0
            )
        context.shared_state[f"{self.name}_ran"] = True
        return TrendStageResult(
            stage_name=self.name, status=TrendStageStatus.SUCCESS, duration_ms=5.0
        )

@pytest.mark.asyncio
async def test_pipeline_ordered_execution(sample_trend_symbols):
    pipeline = TrendPipeline()
    pipeline.register_stage(MockStage("Stage1"))
    pipeline.register_stage(MockStage("Stage2"))
    
    context = TrendExecutionContext(
        run_id="run_1",
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        started_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        configuration_hash="hash",
        pipeline_version="1.0.0",
        schema_version="1.0.0"
    )
    
    result_context = await pipeline.execute(context)
    assert result_context.shared_state["Stage1_ran"] is True
    assert result_context.shared_state["Stage2_ran"] is True
    assert len(result_context.stage_results) == 2

@pytest.mark.asyncio
async def test_pipeline_fail_fast(sample_trend_symbols):
    pipeline = TrendPipeline(fail_fast=True)
    pipeline.register_stage(MockStage("Stage1", should_fail=True))
    pipeline.register_stage(MockStage("Stage2"))
    
    context = TrendExecutionContext(
        run_id="run_1",
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        started_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        configuration_hash="hash",
        pipeline_version="1.0.0",
        schema_version="1.0.0"
    )
    
    with pytest.raises(TrendPipelineError, match="Fail-fast enabled"):
        await pipeline.execute(context)

# --- 5. Repository Tests ---

@pytest.mark.asyncio
async def test_repository_insert_only_and_idempotency(sample_trend_symbols):
    repo = InMemoryTrendRepository()
    snapshot = TrendSnapshot(
        snapshot_id="id_1",
        snapshot_version=1,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1,
        created_at=datetime.now(timezone.utc),
        symbols=sample_trend_symbols,
        pipeline_version="1.0.0",
        configuration_hash="hash_x",
        schema_version="1.0.0",
        execution_metadata={},
        audit_metadata={}
    )
    
    await repo.save_snapshot(snapshot)
    
    # Test duplicate ID
    snapshot2 = snapshot.model_copy(update={"snapshot_version": 2})
    with pytest.raises(DuplicateSnapshotVersionError, match="already exists"):
        await repo.save_snapshot(snapshot2)

    # Test duplicate version
    snapshot3 = snapshot.model_copy(update={"snapshot_id": "id_2"})
    with pytest.raises(DuplicateSnapshotVersionError, match="already exists"):
        await repo.save_snapshot(snapshot3)

def test_exceptions_coverage():
    """Trivially cover custom exceptions."""
    with pytest.raises(TrendRepositoryError):
        raise TrendRepositoryError("test")
    with pytest.raises(MissingIndicatorDataError):
        raise MissingIndicatorDataError("test")
    with pytest.raises(MissingStructureDataError):
        raise MissingStructureDataError("test")
    with pytest.raises(InvalidConfigurationError):
        raise InvalidConfigurationError("test")
    with pytest.raises(InvalidSnapshotLineageError):
        raise InvalidSnapshotLineageError("test")
    with pytest.raises(TrendPipelineExecutionError):
        raise TrendPipelineExecutionError("test")

@pytest.mark.asyncio
async def test_repository_async_concurrency(sample_trend_symbols):
    repo = InMemoryTrendRepository()
    
    async def insert_snap(i: int):
        snap = TrendSnapshot(
            snapshot_id=f"id_{i}",
            snapshot_version=i,
            source_watchlist_snapshot_id="wl_1",
            source_watchlist_version=1,
            source_indicator_snapshot_id="ind_1",
            source_indicator_snapshot_version=1,
            source_structure_snapshot_id="str_1",
            source_structure_snapshot_version=1,
            created_at=datetime.now(timezone.utc),
            symbols=sample_trend_symbols,
            pipeline_version="1.0.0",
            configuration_hash="hash_x",
            schema_version="1.0.0",
            execution_metadata={},
            audit_metadata={}
        )
        await repo.save_snapshot(snap)
        
    await asyncio.gather(*(insert_snap(i) for i in range(1, 101)))
    
    history = await repo.list_snapshot_history(limit=100)
    assert len(history) == 100
    assert history[0].snapshot_version == 100

# --- 6. Engine Integration & Statelessness Tests ---

@pytest.mark.asyncio
async def test_engine_stateless_execution(sample_trend_symbols, trend_settings, snapshot_builder):
    repo = InMemoryTrendRepository()
    validator = TrendValidator()
    pipeline = TrendPipeline()
    
    engine = TrendEngine(
        pipeline=pipeline,
        repository=repo,
        validator=validator,
        snapshot_builder=snapshot_builder,
        settings=trend_settings
    )
    
    # Execute first time
    snap1 = await engine.generate_trend_snapshot(
        symbols=sample_trend_symbols,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1
    )
    
    assert snap1.snapshot_version == 1
    assert snap1.source_watchlist_snapshot_id == "wl_1"
    
    # Execute second time (should auto-increment version deterministically)
    snap2 = await engine.generate_trend_snapshot(
        symbols=sample_trend_symbols,
        source_watchlist_snapshot_id="wl_1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="ind_1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="str_1",
        source_structure_snapshot_version=1
    )
    
    assert snap2.snapshot_version == 2
    assert snap2.source_watchlist_snapshot_id == "wl_1"
    
    # Verify fingerprint stability across identical business inputs
    assert snap1.generate_business_fingerprint() == snap2.generate_business_fingerprint()
