import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.paper_execution_result_engine.contracts.repository import PaperExecutionResultRepository
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultPersistenceError

class PostgreSQLPaperExecutionResultRepository(PaperExecutionResultRepository):
    """
    PostgreSQL persistence for execution results using SQLAlchemy Session.
    """
    def __init__(self, session: Session) -> None:
        self._session = session
        
    def save(self, snapshot: PaperExecutionSnapshot) -> None:
        try:
            if self.exists(snapshot.snapshot_version):
                raise PaperExecutionResultPersistenceError(f"Snapshot {snapshot.snapshot_version} already exists")
                
            stmt = text("""
                INSERT INTO paper_execution_snapshots (
                    snapshot_version, created_at, execution_status, parent_order_snapshot_version,
                    parent_fill_snapshot_version, snapshot_data
                ) VALUES (
                    :version, :created_at, :status, :order_ver, :fill_ver, :data
                )
            """)
            
            self._session.execute(stmt, {
                "version": snapshot.snapshot_version,
                "created_at": snapshot.created_at,
                "status": snapshot.execution_status.value,
                "order_ver": snapshot.parent_order_snapshot_version,
                "fill_ver": snapshot.parent_fill_snapshot_version,
                "data": snapshot.model_dump_json()
            })
            self._session.commit()
        except PaperExecutionResultPersistenceError:
            self._session.rollback()
            raise
        except Exception as e:
            self._session.rollback()
            raise PaperExecutionResultPersistenceError(f"Failed to save snapshot: {e}") from e
            
    def load(self, snapshot_version: str) -> PaperExecutionSnapshot:
        stmt = text("SELECT snapshot_data FROM paper_execution_snapshots WHERE snapshot_version = :ver")
        row = self._session.execute(stmt, {"ver": snapshot_version}).fetchone()
        if not row:
            raise PaperExecutionResultPersistenceError(f"Snapshot version {snapshot_version} not found.")
        
        # Depending on how the database returns JSON, it might be a string or a dict.
        data = row[0] if isinstance(row[0], str) else json.dumps(row[0])
        return PaperExecutionSnapshot.model_validate_json(data)
        
    def exists(self, snapshot_version: str) -> bool:
        stmt = text("SELECT 1 FROM paper_execution_snapshots WHERE snapshot_version = :ver")
        return self._session.execute(stmt, {"ver": snapshot_version}).fetchone() is not None
        
    def load_latest(self) -> Optional[PaperExecutionSnapshot]:
        stmt = text("SELECT snapshot_data FROM paper_execution_snapshots ORDER BY created_at DESC LIMIT 1")
        row = self._session.execute(stmt).fetchone()
        if not row:
            return None
        data = row[0] if isinstance(row[0], str) else json.dumps(row[0])
        return PaperExecutionSnapshot.model_validate_json(data)
        
    def list_all(self) -> List[PaperExecutionSnapshot]:
        stmt = text("SELECT snapshot_data FROM paper_execution_snapshots ORDER BY created_at ASC")
        rows = self._session.execute(stmt).fetchall()
        result = []
        for row in rows:
            data = row[0] if isinstance(row[0], str) else json.dumps(row[0])
            result.append(PaperExecutionSnapshot.model_validate_json(data))
        return result
