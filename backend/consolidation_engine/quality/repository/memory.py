import asyncio
from typing import Dict, List, Optional
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.quality.models import ConsolidationQualityReport, ConsolidationQualityLevel
from backend.consolidation_engine.quality.contracts import IConsolidationQualityRepository

class InMemoryConsolidationQualityRepository(IConsolidationQualityRepository):
    """
    In-memory implementation of IConsolidationQualityRepository.
    """
    
    def __init__(self):
        self._reports: Dict[str, ConsolidationQualityReport] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, report: ConsolidationQualityReport) -> None:
        async with self._lock:
            if report.report_id in self._reports:
                raise ConsolidationRepositoryError(f"Quality report {report.report_id} already exists.")
            self._reports[report.report_id] = report
            
    async def exists(self, report_id: str) -> bool:
        return report_id in self._reports
        
    async def load_by_candidate_id(self, candidate_id: str) -> Optional[ConsolidationQualityReport]:
        # Assume 1:1 mapping between candidate and quality report (latest version if overwriting, but reports are immutable)
        # Actually, candidates are deterministic, so there's usually 1 report per candidate per config.
        # We will return the first matching for simplicity.
        for r in self._reports.values():
            if r.candidate_id == candidate_id:
                return r
        return None
        
    async def query_by_symbol(self, symbol: str) -> List[ConsolidationQualityReport]:
        return [r for r in self._reports.values() if r.symbol == symbol]
        
    async def query_by_timeframe(self, timeframe: str) -> List[ConsolidationQualityReport]:
        return [r for r in self._reports.values() if r.timeframe == timeframe]
        
    async def query_by_quality(self, quality_level: ConsolidationQualityLevel) -> List[ConsolidationQualityReport]:
        return [r for r in self._reports.values() if r.quality_level == quality_level]
