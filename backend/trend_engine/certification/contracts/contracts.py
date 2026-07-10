from abc import ABC, abstractmethod
from typing import Optional, List
from backend.trend_engine.certification.models.models import CertificationReport

class ICertificationStage(ABC):
    """Contract for a specific verification stage in the certification pipeline."""
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the stage."""
        pass

    @abstractmethod
    async def execute(self, context: dict) -> bool:
        """
        Execute the certification stage.
        Must raise a CertificationFailure exception on critical error.
        Returns True if passed, False if conditionally skipped/failed non-critically.
        """
        pass

class ITrendCertificationPipeline(ABC):
    """Contract for orchestrating certification stages."""
    @abstractmethod
    async def run_certification(self) -> CertificationReport:
        """Executes all stages and returns the immutable final report."""
        pass

class ICertificationReportRepository(ABC):
    """Contract for persisting certification reports with INSERT-only semantics."""
    @abstractmethod
    async def exists(self, report_id: str) -> bool:
        """Check if a report exists."""
        pass
        
    @abstractmethod
    async def save(self, report: CertificationReport, report_id: str) -> None:
        """Save a new report. Must raise ImmutabilityViolationError if modifying existing."""
        pass
        
    @abstractmethod
    async def load(self, report_id: str) -> Optional[CertificationReport]:
        """Load a specific report by ID."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[CertificationReport]:
        """Load the most recently saved report."""
        pass
        
    @abstractmethod
    async def query_by_phase(self, phase_version: str) -> List[CertificationReport]:
        """Query reports by phase version (e.g. '7.6')."""
        pass
        
    @abstractmethod
    async def query_by_version(self, pipeline_version: str) -> List[CertificationReport]:
        """Query reports by pipeline version."""
        pass
