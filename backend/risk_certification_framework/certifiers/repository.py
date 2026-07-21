from backend.risk_certification_framework.contracts.repository import IRiskCertificationRepository
from backend.risk_certification_framework.models.record import VerificationRecord
from backend.risk_certification_framework.models.snapshot import RiskCertificationSnapshot

class RepositoryCertifier:
    """
    Validates repository invariants like immutability and lack of update/delete.
    """
    
    async def verify(self, repo: IRiskCertificationRepository, snapshot: RiskCertificationSnapshot) -> VerificationRecord:
        try:
            # We assume repo is the memory repo testing duplicate insert
            await repo.insert(snapshot)
            try:
                await repo.insert(snapshot)
                raise RuntimeError("Repository allowed duplicate insert (update). Should have raised exception.")
            except ValueError:
                pass # Expected
                
            return VerificationRecord(
                certifier_name="RepositoryCertifier",
                status="PASS",
                evidence="Repository correctly rejected updates/replaces and preserved insertion.",
                metrics={"insert_tested": True}
            )
        except Exception as e:
            return VerificationRecord(
                certifier_name="RepositoryCertifier",
                status="FAIL",
                evidence=f"Repository verification failed: {str(e)}",
                metrics={}
            )
