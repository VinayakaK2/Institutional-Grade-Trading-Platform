import pytest
import datetime
import uuid

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol, WatchlistCandidate, WatchlistSnapshot, WatchlistValidationStatus
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistAuditRecord, WatchlistStatus
from backend.watchlist_engine.management.infrastructure.repository import ManagedWatchlistRepository

from backend.watchlist_engine.management.infrastructure.repository import ManagedWatchlistRepository

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.infrastructure.database.orm.base import Base

import pytest_asyncio

@pytest_asyncio.fixture
async def db_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield session_factory
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    
def create_mock_snapshot(version: int, base_snapshot_id: str, fresh_snapshot_id: str, managed_snapshot_id: str) -> ManagedWatchlistSnapshot:
    candidate = WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
            name="Apple Inc",
            sector="Tech"
        )
    )
    base = WatchlistSnapshot(
        snapshot_id=base_snapshot_id,
        version=version,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        symbol_count=1,
        candidates=[candidate],
        metadata={},
        pipeline_version="1.0.0",
        config_hash="hash",
        validation_status=WatchlistValidationStatus.PASSED,
        source_universe_version=version
    )
    fresh = FreshWatchlistSnapshot(
        freshness_snapshot_id=fresh_snapshot_id,
        version=version,
        watchlist_snapshot=base,
        dataset_version="2026-07-07",
        parent_candidate_watchlist_version=str(version)
    )
    return ManagedWatchlistSnapshot(
        managed_snapshot_id=managed_snapshot_id,
        version=version,
        fresh_watchlist_snapshot=fresh,
        parent_fresh_watchlist_version=version,
        parent_candidate_watchlist_version=str(version),
        parent_universe_version=version,
        dataset_version="2026-07-07",
        pipeline_version="1.0.0",
        config_hash="hash",
        business_fingerprint=f"fp_{version}",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        status=WatchlistStatus.VALID
    )

@pytest.mark.asyncio
async def test_save_and_load_managed_snapshot(db_session_factory):
    repo = ManagedWatchlistRepository(db_session_factory)
    
    base_id = str(uuid.uuid4())
    fresh_id = str(uuid.uuid4())
    managed_id = str(uuid.uuid4())
    
    # Needs to insert base and fresh snapshots to DB first due to foreign key constraints
    from backend.infrastructure.database.orm.watchlist import WatchlistSnapshotModel
    from backend.watchlist_engine.freshness.infrastructure.orm import FreshWatchlistSnapshotModel
    
    async with db_session_factory() as session:
        base_model = WatchlistSnapshotModel(
            snapshot_id=base_id,
            version=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            symbol_count=1,
            candidates=[],
            metadata_col={},
            pipeline_version="1.0.0",
            config_hash="hash",
            validation_status="PASSED",
            source_universe_version=1
        )
        fresh_model = FreshWatchlistSnapshotModel(
            freshness_snapshot_id=fresh_id,
            version=1,
            watchlist_snapshot_id=base_id,
            dataset_version="2026-07-07",
            parent_candidate_watchlist_version="1"
        )
        session.add(base_model)
        session.add(fresh_model)
        await session.commit()
    
    snapshot = create_mock_snapshot(1, base_id, fresh_id, managed_id)
    audit = WatchlistAuditRecord(
        event_id=str(uuid.uuid4()),
        managed_snapshot_id=managed_id,
        event_type="CREATED",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metadata={}
    )
    
    await repo.save_managed_snapshot(snapshot, audit)
    
    loaded = await repo.load_latest_managed_snapshot()
    assert loaded is not None
    assert loaded.version == 1
    assert loaded.managed_snapshot_id == managed_id
    assert loaded.business_fingerprint == "fp_1"
    
    history = await repo.get_snapshot_history()
    assert len(history) == 1
    
    audits = await repo.get_audit_history(managed_id)
    assert len(audits) == 1
    assert audits[0].event_type == "CREATED"
