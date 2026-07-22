from typing import Optional
from backend.paper_order_engine.contracts.repository import IPaperOrderRepository
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot

class PostgreSQLPaperOrderRepository(IPaperOrderRepository):
    """
    Skeleton PostgreSQL repository for paper order snapshots.
    Methods match the interface but raise NotImplementedError.
    """
    def save(self, snapshot: PaperOrderSnapshot) -> None:
        raise NotImplementedError("PostgreSQLPaperOrderRepository.save is not implemented yet.")

    def load(self, snapshot_id: str) -> Optional[PaperOrderSnapshot]:
        raise NotImplementedError("PostgreSQLPaperOrderRepository.load is not implemented yet.")

    def exists(self, snapshot_id: str) -> bool:
        raise NotImplementedError("PostgreSQLPaperOrderRepository.exists is not implemented yet.")

    def load_latest(self) -> Optional[PaperOrderSnapshot]:
        raise NotImplementedError("PostgreSQLPaperOrderRepository.load_latest is not implemented yet.")

    def load_by_snapshot_version(self, version: str) -> Optional[PaperOrderSnapshot]:
        raise NotImplementedError("PostgreSQLPaperOrderRepository.load_by_snapshot_version is not implemented yet.")
