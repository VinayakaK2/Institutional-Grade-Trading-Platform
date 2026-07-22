import pytest
from backend.portfolio_certification_framework.repository.memory_repo import MemoryPortfolioCertificationRepository
from backend.portfolio_certification_framework.services.query_service import PortfolioCertificationQueryService
from unittest.mock import MagicMock
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot

@pytest.mark.asyncio
async def test_repository_save_load():
    repo = MemoryPortfolioCertificationRepository()
    snap = MagicMock(spec=PortfolioCertificationSnapshot)
    snap.snapshot_id = "123"
    
    await repo.save(snap)
    loaded = await repo.load("123")
    assert loaded.snapshot_id == "123"
    assert await repo.exists("123")
    
@pytest.mark.asyncio
async def test_query_service_load_latest():
    repo = MemoryPortfolioCertificationRepository()
    svc = PortfolioCertificationQueryService(repository=repo)
    snap = MagicMock(spec=PortfolioCertificationSnapshot)
    snap.snapshot_id = "123"
    
    await repo.save(snap)
    
    latest = await svc.load_latest()
    assert latest.snapshot_id == "123"
