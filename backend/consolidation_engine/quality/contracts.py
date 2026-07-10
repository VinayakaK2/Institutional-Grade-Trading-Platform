from abc import ABC, abstractmethod
from typing import List, Optional
from backend.consolidation_engine.quality.models import ConsolidationQualityReport, ConsolidationQualityLevel

class IConsolidationQualityRepository(ABC):
    """
    Contract for immutable, INSERT-only repository for Consolidation Quality Reports.
    """
    
    @abstractmethod
    async def save(self, report: ConsolidationQualityReport) -> None:
        """
        Idempotent insert of a quality report.
        Raises an error if report_id already exists.
        """
        pass
        
    @abstractmethod
    async def exists(self, report_id: str) -> bool:
        """Checks if a report exists."""
        pass
        
    @abstractmethod
    async def load_by_candidate_id(self, candidate_id: str) -> Optional[ConsolidationQualityReport]:
        """Loads the report for a specific candidate."""
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[ConsolidationQualityReport]:
        """Loads all reports for a symbol."""
        pass
        
    @abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[ConsolidationQualityReport]:
        """Loads all reports for a given timeframe."""
        pass
        
    @abstractmethod
    async def query_by_quality(self, quality_level: ConsolidationQualityLevel) -> List[ConsolidationQualityReport]:
        """Loads all reports that achieved a specific quality level."""
        pass
