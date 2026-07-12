from typing import List, Optional
from backend.liquidity_grab_engine.certification.models.models import CertificationReport, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.contracts.repository import ICertificationRepository

class PostgreSQLCertificationRepository(ICertificationRepository):
    """
    Stub for a PostgreSQL-backed Certification Repository.
    """
    
    async def save(self, report: CertificationReport) -> None:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
        
    async def load(self, report_id: str) -> Optional[CertificationReport]:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
        
    async def exists(self, report_id: str) -> bool:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
        
    async def load_latest(self) -> Optional[CertificationReport]:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
        
    async def query_by_phase(self, phase: CertificationPhaseEnum) -> List[CertificationReport]:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
        
    async def query_by_version(self, dataset_version: str) -> List[CertificationReport]:
        raise NotImplementedError("PostgreSQL implementation not yet built.")
