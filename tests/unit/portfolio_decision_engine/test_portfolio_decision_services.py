import pytest
from backend.portfolio_decision_engine.repository.memory_repo import MemoryPortfolioDecisionRepository
from backend.portfolio_decision_engine.services.query_service import PortfolioDecisionQueryService
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot
from unittest.mock import MagicMock

def test_repository_save_and_load():
    repo = MemoryPortfolioDecisionRepository()
    snapshot = MagicMock(spec=PortfolioDecisionSnapshot)
    snapshot.snapshot_id = "snap_1"
    snapshot.business_fingerprint = "fp_1"
    
    repo.save(snapshot)
    
    assert repo.exists("snap_1")
    assert repo.load("snap_1") == snapshot
    
    # Should not allow duplicate inserts
    with pytest.raises(ValueError):
        repo.save(snapshot)

def test_repository_latest():
    repo = MemoryPortfolioDecisionRepository()
    snap1 = MagicMock(spec=PortfolioDecisionSnapshot)
    snap1.snapshot_id = "snap_1"
    
    snap2 = MagicMock(spec=PortfolioDecisionSnapshot)
    snap2.snapshot_id = "snap_2"
    
    repo.save(snap1)
    repo.save(snap2)
    
    assert repo.load_latest() == snap2

def test_repository_load_by_business_fingerprint():
    repo = MemoryPortfolioDecisionRepository()
    snap1 = MagicMock(spec=PortfolioDecisionSnapshot)
    snap1.snapshot_id = "snap_1"
    snap1.business_fingerprint = "fp_1"
    
    repo.save(snap1)
    assert repo.load_by_business_fingerprint("fp_1") == snap1
    assert repo.load_by_business_fingerprint("fp_2") is None

def test_query_service():
    repo = MemoryPortfolioDecisionRepository()
    snap = MagicMock(spec=PortfolioDecisionSnapshot)
    snap.snapshot_id = "snap_1"
    snap.business_fingerprint = "fp_1"
    repo.save(snap)
    
    service = PortfolioDecisionQueryService(repo)
    assert service.get_snapshot("snap_1") == snap
    assert service.get_latest() == snap
    assert service.get_by_business_fingerprint("fp_1") == snap
