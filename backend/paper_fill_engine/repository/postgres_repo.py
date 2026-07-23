from typing import Optional
from backend.paper_fill_engine.contracts.repository import IPaperFillRepository
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot

class PostgreSQLPaperFillRepository(IPaperFillRepository):
    """
    Skeleton PostgreSQL repository for paper fill snapshots.
    Methods match the interface but raise NotImplementedError.
    """
    def save(self, snapshot: PaperFillSnapshot) -> None:
        raise NotImplementedError("PostgreSQLPaperFillRepository.save is not implemented yet.")

    def load(self, snapshot_id: str) -> Optional[PaperFillSnapshot]:
        raise NotImplementedError("PostgreSQLPaperFillRepository.load is not implemented yet.")

    def exists(self, snapshot_id: str) -> bool:
        raise NotImplementedError("PostgreSQLPaperFillRepository.exists is not implemented yet.")

    def load_latest(self) -> Optional[PaperFillSnapshot]:
        raise NotImplementedError("PostgreSQLPaperFillRepository.load_latest is not implemented yet.")
