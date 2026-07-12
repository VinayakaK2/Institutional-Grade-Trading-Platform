from typing import List, Optional, Dict
from backend.liquidity_grab_engine.certification.models.models import CertificationReport, CertificationPhaseEnum
from backend.liquidity_grab_engine.certification.contracts.repository import ICertificationRepository

class InMemoryCertificationRepository(ICertificationRepository):
    """
    In-memory implementation of the Certification Repository for testing and local execution.
    """
    
    def __init__(self) -> None:
        self._reports: Dict[str, CertificationReport] = {}
        self._latest_id: Optional[str] = None
        
    async def save(self, report: CertificationReport) -> None:
        if report.report_id in self._reports:
            raise ValueError(f"Report {report.report_id} already exists. Repository is insert-only.")
            
        self._reports[report.report_id] = report
        self._latest_id = report.report_id
        
    async def load(self, report_id: str) -> Optional[CertificationReport]:
        return self._reports.get(report_id)
        
    async def exists(self, report_id: str) -> bool:
        return report_id in self._reports
        
    async def load_latest(self) -> Optional[CertificationReport]:
        if not self._latest_id:
            return None
        return self._reports.get(self._latest_id)
        
    async def query_by_phase(self, phase: CertificationPhaseEnum) -> List[CertificationReport]:
        results = []
        for report in self._reports.values():
            for pr in report.summary.phase_results:
                if pr.phase == phase:
                    results.append(report)
                    break
        return results
        
    async def query_by_version(self, dataset_version: str) -> List[CertificationReport]:
        results = []
        for report in self._reports.values():
            if report.dataset_metadata.get("dataset_version") == dataset_version:
                results.append(report)
        return results
