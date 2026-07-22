from backend.portfolio_certification_framework.contracts.repository import IPortfolioCertificationRepository
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot

class PortfolioCertificationQueryService:
    """
    Read-only service facade over the repository.
    """
    def __init__(self, repository: IPortfolioCertificationRepository):
        self._repository = repository
        
    async def load_latest(self) -> PortfolioCertificationSnapshot:
        return await self._repository.load_latest()
        
    async def query_by_dataset_version(self, dataset_version: str):
        raise NotImplementedError("Advanced queries are pending infrastructure implementation.")
        
    async def query_by_parent_snapshot(self, parent_id: str):
        raise NotImplementedError("Advanced queries are pending infrastructure implementation.")
        
    async def query_by_time_range(self, start_time: str, end_time: str):
        raise NotImplementedError("Advanced queries are pending infrastructure implementation.")
