from abc import ABC, abstractmethod
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot

class IPortfolioCertificationRepository(ABC):
    @abstractmethod
    async def save(self, snapshot: PortfolioCertificationSnapshot) -> None:
        """Saves a new snapshot. Insert-only. Should raise ValueError if duplicate exists."""
        pass

    @abstractmethod
    async def load(self, snapshot_id: str) -> PortfolioCertificationSnapshot:
        """Loads a snapshot by ID. Raises ValueError if missing."""
        pass

    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        """Checks if a snapshot exists by ID."""
        pass

    @abstractmethod
    async def load_latest(self) -> PortfolioCertificationSnapshot:
        """Loads the most recently saved snapshot."""
        pass
