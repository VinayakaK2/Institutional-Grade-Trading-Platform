from typing import List
from backend.paper_execution_certification_engine.engine.stages.base import ICertificationStage
from backend.paper_execution_certification_engine.models.snapshot import StageResult
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.repository.memory_repo import MemoryPaperExecutionCertificationRepository

class RepositoryVerificationStage(ICertificationStage):
    """
    Verifies repository invariants. Proves immutability by testing that 
    duplicate saves do not overwrite and historical snapshots are unmodified.
    """
    
    @property
    def name(self) -> str:
        return "Repository Verification"
        
    async def _run_verification(self, context: PaperExecutionCertificationContext, previous_results: List[StageResult]) -> dict:
        from backend.paper_execution_certification_engine.repository.memory_repo import MemoryPaperExecutionCertificationRepository
        from backend.paper_execution_certification_engine.models.snapshot import PaperExecutionCertificationSnapshot, CertificationReport, CertificationMetadata
        from backend.paper_execution_certification_engine.exceptions.exceptions import CertificationRepositoryIntegrityError, CertificationFailedError
        
        from datetime import datetime, timezone
        
        repo = MemoryPaperExecutionCertificationRepository()
        
        report = CertificationReport(
            certification_id="cert-repo-test",
            certification_schema_version="1.0.0",
            certified=True,
            paper_execution_version="1.0",
            optimization_version="1.0",
            certification_version="1.0",
            timestamp="2026-07-23T00:00:00Z",
            business_fingerprint="bfp",
            canonical_hash="ch",
            evidence_count=0,
            verified_stages=[]
        )
        
        now = datetime.now(timezone.utc)
        
        snap1 = PaperExecutionCertificationSnapshot(
            snapshot_version="v1",
            certification_id="cert-repo-test-1",
            certification_version="1.0",
            certification_report=report,
            business_fingerprint="bfp1",
            canonical_hash="ch1",
            parent_execution_snapshot_version="p1",
            certification_metadata=CertificationMetadata(certified_at=now, execution_duration_ms=10.0)
        )
        
        snap2 = PaperExecutionCertificationSnapshot(
            snapshot_version="v2",
            certification_id="cert-repo-test-2",
            certification_version="1.0",
            certification_report=report,
            business_fingerprint="bfp2",
            canonical_hash="ch2",
            parent_execution_snapshot_version="p1",
            certification_metadata=CertificationMetadata(certified_at=now, execution_duration_ms=10.0)
        )
        
        # 1. Insert snap1
        await repo.save(snap1)
        
        # 2. Insert snap2
        await repo.save(snap2)
        
        # 3. Load oldest (v1) and verify byte-for-byte unchanged
        loaded_snap1 = await repo.load("v1")
        if loaded_snap1.model_dump_json() != snap1.model_dump_json():
            raise CertificationFailedError("Repository immutability broken: oldest snapshot changed")
            
        # 4. Load newest (p1)
        loaded_latest = await repo.load_latest("p1")
        if loaded_latest is None or loaded_latest.snapshot_version != "v2":
            raise CertificationFailedError("Repository load_latest failed")
            
        # 5. Duplicate save fails
        try:
            await repo.save(snap1)
            raise CertificationFailedError("Repository allowed duplicate save")
        except CertificationRepositoryIntegrityError:
            pass # Expected
            
        return {
            "duplicate_saves_prevented": True,
            "oldest_snapshot_verified": True,
            "newest_snapshot_verified": True,
            "historical_immutability_verified": True
        }
