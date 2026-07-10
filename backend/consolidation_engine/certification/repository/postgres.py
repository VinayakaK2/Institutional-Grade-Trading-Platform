from typing import List, Optional
from backend.consolidation_engine.certification.models import ConsolidationCertificationReport
from backend.consolidation_engine.certification.contracts import IConsolidationCertificationRepository

class PostgreSQLConsolidationCertificationRepository(IConsolidationCertificationRepository):
    """
    PostgreSQL stub for certification reports.
    """
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
        
    async def save(self, report: ConsolidationCertificationReport) -> None:
        pass
        
    async def exists(self, certification_id: str) -> bool:
        return False
        
    async def load(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        return None
        
    async def load_latest(self) -> Optional[ConsolidationCertificationReport]:
        return None
        
    async def query_by_certification_id(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        return None
        
    async def query_by_pipeline_version(self, pipeline_version: str) -> List[ConsolidationCertificationReport]:
        return []
        
    async def query_by_business_fingerprint_version(self, fingerprint_version: str) -> List[ConsolidationCertificationReport]:
        return []
