import abc
from typing import Dict, Any
from backend.trade_validation_engine.certification.models.models import CertificationReport

class ICertificationRepository(abc.ABC):
    """
    Repository for persisting the final Certification Report and its raw evidence.
    """
    @abc.abstractmethod
    async def save_report(self, report: CertificationReport) -> None:
        pass
        
    @abc.abstractmethod
    async def save_evidence(self, stage_name: str, evidence: Dict[str, Any]) -> str:
        """
        Saves raw JSON evidence and returns the path to the stored file.
        """
        pass
