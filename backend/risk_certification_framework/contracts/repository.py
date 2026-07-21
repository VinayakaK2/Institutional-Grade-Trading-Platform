from abc import ABC, abstractmethod
from backend.risk_certification_framework.models.snapshot import RiskCertificationSnapshot

class IRiskCertificationRepository(ABC):
    """
    INSERT-Only Repository for RiskCertificationSnapshots.
    """
    
    @abstractmethod
    async def insert(self, snapshot: RiskCertificationSnapshot) -> None:
        """
        Inserts a new immutable certification snapshot.
        """
        pass
        
    @abstractmethod
    async def get(self, snapshot_id: str) -> RiskCertificationSnapshot:
        """
        Reads a certification snapshot by its ID.
        """
        pass
