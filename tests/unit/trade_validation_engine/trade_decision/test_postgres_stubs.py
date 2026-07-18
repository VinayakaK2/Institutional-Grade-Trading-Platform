import pytest
from backend.trade_validation_engine.trade_decision.repository.postgres import PostgresTradeDecisionRepository
from backend.trade_validation_engine.trade_decision.query_service.postgres import PostgresTradeDecisionQueryService

@pytest.mark.asyncio
async def test_postgres_stubs():
    repo = PostgresTradeDecisionRepository("dummy")
    with pytest.raises(NotImplementedError):
        await repo.save(None)
    with pytest.raises(NotImplementedError):
        await repo.load("id")
    with pytest.raises(NotImplementedError):
        await repo.exists("id")
    with pytest.raises(NotImplementedError):
        await repo.query_by_symbol("sym")
    with pytest.raises(NotImplementedError):
        await repo.query_by_timeframe("1H")
    with pytest.raises(NotImplementedError):
        await repo.query_by_dataset_version(1)
    with pytest.raises(NotImplementedError):
        await repo.query_by_validation_report("rep")
    with pytest.raises(NotImplementedError):
        await repo.load_latest("sym", "1H")

@pytest.mark.asyncio
async def test_postgres_query_service_stubs():
    svc = PostgresTradeDecisionQueryService("dummy")
    with pytest.raises(NotImplementedError):
        await svc.get_by_decision_id("id")
    with pytest.raises(NotImplementedError):
        await svc.get_latest_by_symbol("sym")
    with pytest.raises(NotImplementedError):
        await svc.query_by_dataset_version(1)
