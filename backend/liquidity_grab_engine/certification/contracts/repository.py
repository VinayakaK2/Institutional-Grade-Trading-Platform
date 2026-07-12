from abc import ABC, abstractmethod
from typing import List, Optional
from backend.liquidity_grab_engine.certification.models.models import CertificationReport, CertificationPhaseEnum

class ICertificationRepository(ABC):
    """
    Contract for persisting and retrieving Certification Reports.
    Must remain INSERT-only. Must not mutate existing reports.
    """
    
    @abstractmethod
    async def save(self, report: CertificationReport) -> None:
        """Saves a new certification report."""
        pass
        
    @abstractmethod
    async def load(self, report_id: str) -> Optional[CertificationReport]:
        """Loads a certification report by ID."""
        pass
        
    @abstractmethod
    async def exists(self, report_id: str) -> bool:
        """Checks if a report exists by ID."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[CertificationReport]:
        """Loads the most recently saved certification report."""
        pass
        
    @abstractmethod
    async def query_by_phase(self, phase: CertificationPhaseEnum) -> List[CertificationReport]:
        """Queries reports that include the specified phase in their results."""
        pass
        
    @abstractmethod
    async def query_by_version(self, dataset_version: str) -> List[CertificationReport]:
        """Queries reports based on dataset version."""
        pass
