from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
import json
import asyncio

from backend.paper_execution_optimization_engine.contracts.repository import IPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot
from backend.paper_execution_optimization_engine.repository.memory_repo import OptimizationRepositoryIntegrityError, OptimizationRepositoryNotFoundError


class PostgreSQLPaperExecutionOptimizationRepository(IPaperExecutionOptimizationRepository):
    """
    Synchronous SQLAlchemy-based PostgreSQL repository using threading to avoid blocking the event loop.
    Enforces append-only through strict INSERT without pre-checking exists, relying on DB integrity.
    """
    
    def __init__(self, engine: Engine):
        self._engine = engine
        
    async def save(self, snapshot: PaperExecutionOptimizationSnapshot) -> None:
        def _save():
            sql = text("""
                INSERT INTO paper_execution_optimization_snapshots 
                (optimization_fingerprint, snapshot_version, data)
                VALUES (:optimization_fingerprint, :snapshot_version, :data)
            """)
            
            with self._engine.begin() as conn:
                try:
                    conn.execute(sql, {
                        "optimization_fingerprint": snapshot.optimization_fingerprint,
                        "snapshot_version": snapshot.snapshot_version,
                        "data": snapshot.model_dump_json()
                    })
                except IntegrityError as e:
                    raise OptimizationRepositoryIntegrityError(f"Duplicate INSERT: {snapshot.optimization_fingerprint}") from e
                    
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _save)

    async def save_many(self, snapshots: List[PaperExecutionOptimizationSnapshot]) -> None:
        if not snapshots:
            return
            
        def _save_many():
            sql = text("""
                INSERT INTO paper_execution_optimization_snapshots 
                (optimization_fingerprint, snapshot_version, data)
                VALUES (:optimization_fingerprint, :snapshot_version, :data)
            """)
            
            # Using executemany pattern with list of dicts
            params = [
                {
                    "optimization_fingerprint": s.optimization_fingerprint,
                    "snapshot_version": s.snapshot_version,
                    "data": s.model_dump_json()
                } for s in snapshots
            ]
            
            with self._engine.begin() as conn:
                try:
                    conn.execute(sql, params)
                except IntegrityError as e:
                    raise OptimizationRepositoryIntegrityError("Duplicate INSERT within batch") from e
                    
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _save_many)

    async def load(self, optimization_fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        def _load():
            sql = text("""
                SELECT data FROM paper_execution_optimization_snapshots
                WHERE optimization_fingerprint = :optimization_fingerprint
            """)
            
            with self._engine.connect() as conn:
                result = conn.execute(sql, {"optimization_fingerprint": optimization_fingerprint}).fetchone()
                
                if not result:
                    raise OptimizationRepositoryNotFoundError(f"Not found: {optimization_fingerprint}")
                    
                data = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                return PaperExecutionOptimizationSnapshot(**data)
                
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _load)

    async def load_latest(self) -> Optional[PaperExecutionOptimizationSnapshot]:
        def _load_latest():
            sql = text("""
                SELECT data FROM paper_execution_optimization_snapshots
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            with self._engine.connect() as conn:
                result = conn.execute(sql).fetchone()
                
                if not result:
                    return None
                    
                data = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                return PaperExecutionOptimizationSnapshot(**data)
                
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _load_latest)
