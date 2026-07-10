from abc import ABC, abstractmethod
from typing import Optional, List
from backend.consolidation_engine.certification.models import ConsolidationCertificationReport

class IConsolidationCertificationRepository(ABC):
    """
    Contract for immutable, INSERT-only repository for Consolidation Certification Reports.
    """
    
    @abstractmethod
    async def save(self, report: ConsolidationCertificationReport) -> None:
        """Idempotent insert of a certification report."""
        pass
        
    @abstractmethod
    async def exists(self, certification_id: str) -> bool:
        """Checks if a report exists by certification ID."""
        pass
        
    @abstractmethod
    async def load(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        """Loads a specific certification report by its ID."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[ConsolidationCertificationReport]:
        """Loads the most recently generated certification report."""
        pass
        
    @abstractmethod
    async def query_by_certification_id(self, certification_id: str) -> Optional[ConsolidationCertificationReport]:
        """Loads a specific certification report by its ID."""
        pass
        
    @abstractmethod
    async def query_by_pipeline_version(self, pipeline_version: str) -> List[ConsolidationCertificationReport]:
        """Loads all reports for a specific pipeline version."""
        pass
        
    @abstractmethod
    async def query_by_business_fingerprint_version(self, fingerprint_version: str) -> List[ConsolidationCertificationReport]:
        """Loads all reports for a specific fingerprint version."""
        pass
