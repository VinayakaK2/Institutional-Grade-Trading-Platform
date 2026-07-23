from typing import Optional
from backend.paper_execution_certification_engine.contracts.repository import IPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.models.snapshot import PaperExecutionCertificationSnapshot

class PaperExecutionCertificationQueryService:
    """
    Read-only CQRS service for accessing certification reports and snapshots.
    """
    
    def __init__(self, repository: IPaperExecutionCertificationRepository):
        self._repository = repository
        
    async def query_by_execution_snapshot(self, execution_snapshot_version: str) -> Optional[PaperExecutionCertificationSnapshot]:
        """Queries the latest certification for a given execution snapshot."""
        return await self._repository.load_latest(execution_snapshot_version)
        
    async def query_by_certification_version(self, certification_snapshot_version: str) -> Optional[PaperExecutionCertificationSnapshot]:
        """Queries a specific certification snapshot."""
        try:
            return await self._repository.load(certification_snapshot_version)
        except Exception:
            return None
            
    async def query_by_symbol(self, symbol: str) -> list:
        """
        Queries certifications by symbol.
        Since certifications are aggregated over execution snapshots, this requires 
        joining or indexing on business metadata, which is beyond memory mock scope, 
        but included in the interface contract.
        """
        raise NotImplementedError("Query by symbol requires database indices.")
