import pytest
from backend.trade_validation_engine.validation_rules.repository.postgres import PostgresValidationReportRepository
from backend.trade_validation_engine.validation_rules.query_service.postgres import PostgresValidationQueryService

@pytest.mark.asyncio
async def test_postgres_repository_stubs():
    repo = PostgresValidationReportRepository("dummy")
    await repo.save(None)
    assert await repo.load("id") is None
    assert await repo.exists("id") is False
    assert await repo.query_by_symbol("sym") == []
    assert await repo.query_by_timeframe("1H") == []
    assert await repo.query_by_dataset_version(1) == []
    assert await repo.query_by_parent_snapshot("parent") == []
    assert await repo.load_latest("sym", "1H") is None

@pytest.mark.asyncio
async def test_postgres_query_service_stubs():
    svc = PostgresValidationQueryService("dummy")
    assert await svc.get_by_validation_id("id") is None
    assert await svc.get_latest_by_symbol("sym") is None
    assert await svc.query_by_dataset_version(1) == []
    assert await svc.query_by_validation_status(True) == []
