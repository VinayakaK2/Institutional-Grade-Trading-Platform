from typing import List, Optional
from backend.consolidation_engine.quality.contracts import IConsolidationQualityRepository
from backend.consolidation_engine.quality.models import ConsolidationQualityReport, ConsolidationQualityLevel

class ConsolidationQualityQueryService:
    """
    Query service for Consolidation Quality Reports.
    Application code should consume this instead of direct repository access.
    """
    
    def __init__(self, repository: IConsolidationQualityRepository):
        self.repository = repository
        
    async def load_by_candidate_id(self, candidate_id: str) -> Optional[ConsolidationQualityReport]:
        return await self.repository.load_by_candidate_id(candidate_id)
        
    async def latest_reports(self, limit: int = 10) -> List[ConsolidationQualityReport]:
        """
        Loads the latest reports. 
        In a real implementation, this would sort by generated_timestamp.
        Since we only have limited query methods in the repo stub, we might just return empty or 
        rely on an extended repo method. For Phase 8.3 boundaries, we'll stub it.
        """
        # A real implementation would execute a specific query on the repo.
        return []
        
    async def historical_reports(self, limit: int = 50) -> List[ConsolidationQualityReport]:
        return []
        
    async def highest_quality(self, symbol: Optional[str] = None) -> List[ConsolidationQualityReport]:
        """
        Returns reports with EXCELLENT quality.
        If symbol is provided, filters by symbol.
        """
        reports = await self.repository.query_by_quality(ConsolidationQualityLevel.EXCELLENT)
        if symbol:
            reports = [r for r in reports if r.symbol == symbol]
        return reports
        
    async def lowest_quality(self, symbol: Optional[str] = None) -> List[ConsolidationQualityReport]:
        """
        Returns reports with REJECTED quality.
        """
        reports = await self.repository.query_by_quality(ConsolidationQualityLevel.REJECTED)
        if symbol:
            reports = [r for r in reports if r.symbol == symbol]
        return reports
