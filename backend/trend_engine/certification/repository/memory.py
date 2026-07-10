from typing import Dict, Optional, List
from backend.trend_engine.certification.models.models import CertificationReport
from backend.trend_engine.certification.contracts.contracts import ICertificationReportRepository
from backend.trend_engine.certification.exceptions import ImmutabilityViolationError

class InMemoryCertificationReportRepository(ICertificationReportRepository):
    """In-memory implementation of the certification report repository."""
    def __init__(self):
        self._reports: Dict[str, CertificationReport] = {}
        self._latest_id: Optional[str] = None
        
    async def exists(self, report_id: str) -> bool:
        return report_id in self._reports
        
    async def save(self, report: CertificationReport, report_id: str) -> None:
        if await self.exists(report_id):
            raise ImmutabilityViolationError(f"Report {report_id} already exists. Certification reports are immutable.")
            
        self._reports[report_id] = report
        self._latest_id = report_id
        
    async def load(self, report_id: str) -> Optional[CertificationReport]:
        return self._reports.get(report_id)
        
    async def load_latest(self) -> Optional[CertificationReport]:
        if not self._latest_id:
            return None
        return self._reports.get(self._latest_id)
        
    async def query_by_phase(self, phase_version: str) -> List[CertificationReport]:
        return [r for r in self._reports.values() if r.phase_version == phase_version]
        
    async def query_by_version(self, pipeline_version: str) -> List[CertificationReport]:
        return [r for r in self._reports.values() if r.pipeline_version == pipeline_version]
