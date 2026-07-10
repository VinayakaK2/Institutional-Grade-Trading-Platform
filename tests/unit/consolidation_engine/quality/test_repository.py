import pytest
import asyncio
from datetime import datetime, timezone
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.quality.models import (
    ConsolidationQualityReport, ConsolidationQualityMetrics, ConsolidationQualityLevel
)
from backend.consolidation_engine.quality.repository.memory import InMemoryConsolidationQualityRepository
from backend.consolidation_engine.quality.repository.postgres import PostgreSQLConsolidationQualityRepository
from backend.consolidation_engine.quality.services import ConsolidationQualityQueryService

@pytest.fixture
def sample_report():
    metrics = ConsolidationQualityMetrics(
        range_stability=1.0,
        boundary_respect=1.0,
        price_containment=1.0,
        candle_consistency=1.0,
        consolidation_duration=2,
        range_symmetry=1.0
    )
    return ConsolidationQualityReport(
        report_id="r1", candidate_id="id1", symbol="AAPL:NASDAQ", timeframe="1d",
        metrics=metrics, quality_level=ConsolidationQualityLevel.EXCELLENT,
        config_version=1, algorithm_version="1.0"
    )

@pytest.mark.asyncio
async def test_memory_repo(sample_report):
    repo = InMemoryConsolidationQualityRepository()
    
    assert await repo.exists("r1") is False
    await repo.save(sample_report)
    assert await repo.exists("r1") is True
    
    with pytest.raises(ConsolidationRepositoryError):
        await repo.save(sample_report)
        
    loaded = await repo.load_by_candidate_id("id1")
    assert loaded == sample_report
    
    syms = await repo.query_by_symbol("AAPL:NASDAQ")
    assert len(syms) == 1
    
    tfs = await repo.query_by_timeframe("1d")
    assert len(tfs) == 1
    
    qs = await repo.query_by_quality(ConsolidationQualityLevel.EXCELLENT)
    assert len(qs) == 1
    
@pytest.mark.asyncio
async def test_postgres_repo_stub(sample_report):
    repo = PostgreSQLConsolidationQualityRepository(None)
    await repo.save(sample_report)
    assert await repo.exists("r1") is False
    assert await repo.load_by_candidate_id("id1") is None
    assert await repo.query_by_symbol("AAPL:NASDAQ") == []
    assert await repo.query_by_timeframe("1d") == []
    assert await repo.query_by_quality(ConsolidationQualityLevel.EXCELLENT) == []

@pytest.mark.asyncio
async def test_query_service(sample_report):
    repo = InMemoryConsolidationQualityRepository()
    await repo.save(sample_report)
    service = ConsolidationQualityQueryService(repository=repo)
    
    assert await service.load_by_candidate_id("id1") == sample_report
    assert len(await service.latest_reports()) == 0  # Stub
    assert len(await service.historical_reports()) == 0  # Stub
    
    high = await service.highest_quality()
    assert len(high) == 1
    high_sym = await service.highest_quality("AAPL:NASDAQ")
    assert len(high_sym) == 1
    high_sym_none = await service.highest_quality("MSFT:NASDAQ")
    assert len(high_sym_none) == 0
    
    low = await service.lowest_quality()
    assert len(low) == 0
