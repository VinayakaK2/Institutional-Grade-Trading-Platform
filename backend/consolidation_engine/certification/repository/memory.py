import asyncio
from typing import Dict, List, Optional
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.certification.models import ConsolidationCertificationReport
from backend.consolidation_engine.certification.contracts import IConsolidationCertificationRepository

class InMemoryConsolidationCertificationRepository(IConsolidationCertificationRepository):
    """
    In-memory implementation for certification reports.
    """
    
    def __init__(self):
        self._reports: Dict[str, ConsolidationCertificationReport] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, report: ConsolidationCertificationReport) -> None:
        async with self._lock:
            if report.certification_id in self._reports:
                raise ConsolidationRepositoryError(f"Certification report {report.certification_id} already exists.")
            self._reports[report.certification_id] = report
            
    async def exists(self, certification_id: str) -> bool:
        return certification_id in self._reports
        
    async def load(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        return self._reports.get(certification_id)
        
    async def load_latest(self) -> Optional[ConsolidationCertificationReport]:
        if not self._reports:
            return None
        return max(self._reports.values(), key=lambda r: r.generated_timestamp)
        
    async def query_by_certification_id(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        return await self.load(certification_id)
        
    async def query_by_pipeline_version(self, pipeline_version: str) -> List[ConsolidationCertificationReport]:
        return [r for r in self._reports.values() if r.pipeline_version == pipeline_version]
        
    async def query_by_business_fingerprint_version(self, fingerprint_version: str) -> List[ConsolidationCertificationReport]:
        return [r for r in self._reports.values() if r.business_fingerprint_version == fingerprint_version]
