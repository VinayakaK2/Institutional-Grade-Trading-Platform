
import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.services.query import ConsolidationQueryService
from backend.consolidation_engine.repository.memory import InMemoryConsolidationRepository
from backend.consolidation_engine.models.models import ConsolidationSnapshot, ConsolidationCandidate

@pytest.mark.asyncio
async def test_query_service():
    repo = InMemoryConsolidationRepository()
    service = ConsolidationQueryService(repo)
    
    candidate = ConsolidationCandidate(
        candidate_id="id1",
        symbol="AAPL",
        timeframe="1d",
        start_timestamp=datetime.now(timezone.utc),
        end_timestamp=datetime.now(timezone.utc),
        upper_boundary=10,
        lower_boundary=1,
        midpoint=5.5,
        duration=0,
        candle_count=2
    )
    
    snapshot = ConsolidationSnapshot(
        snapshot_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_version=1,
        config_hash="abc",
        business_fingerprint="fp1",
        fingerprint_algorithm_version=1,
        candidates=[candidate]
    )
    
    await repo.save_snapshot(snapshot)
    
    latest = await service.get_latest_snapshot()
    assert latest is not None
    assert latest.snapshot_version == 1
    
    by_version = await service.get_snapshot_by_version(1)
    assert by_version is not None
    assert by_version.snapshot_version == 1
    
    hist = await service.get_historical_snapshots()
    assert len(hist) == 1
    
    active = await service.get_active_consolidations("AAPL", "1d")
    assert len(active) == 1
    assert active[0].symbol == "AAPL"
    
    empty_active = await service.get_active_consolidations("MSFT", "1d")
    assert len(empty_active) == 0

@pytest.mark.asyncio
async def test_query_service_empty():
    repo = InMemoryConsolidationRepository()
    service = ConsolidationQueryService(repo)
    
    active = await service.get_active_consolidations("AAPL", "1d")
    assert len(active) == 0
