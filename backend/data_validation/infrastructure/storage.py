"""
Quarantine Store Adapter
"""
from typing import List, Any
import logging
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from backend.data_validation.contracts.storage import QuarantineStorageContract
from backend.historical_data.models.raw import RawCandle
from backend.infrastructure.database.orm.candle import QuarantinedCandleOrm
from backend.application.uow.base import BaseUnitOfWork
from backend.historical_data.exceptions import StorageException

logger = logging.getLogger(__name__)

class PostgreSQLQuarantineStorage(QuarantineStorageContract):
    def __init__(self, uow: BaseUnitOfWork):
        self._uow = uow
        
    def _get_insert_stmt(self, dialect_name: str, table, values: list, index_elements: list) -> Any:
        if dialect_name == "sqlite":
            s_stmt = sqlite_insert(table).values(values)
            return s_stmt.on_conflict_do_nothing(index_elements=index_elements)
        else:
            p_stmt = pg_insert(table).values(values)
            return p_stmt.on_conflict_do_nothing(index_elements=index_elements)

    async def save_quarantined_candles(self, candles: List[RawCandle], reason: str = "Validation Failed") -> None:
        if not candles:
            return
            
        values = []
        for c in candles:
            values.append({
                "provider": c.provider,
                "symbol_id": c.symbol.symbol,
                "timeframe": c.timeframe.value,
                "raw_timestamp": str(c.raw_timestamp),
                "raw_open": float(c.raw_open) if c.raw_open is not None else 0.0, # Just for storage if None
                "raw_high": float(c.raw_high) if c.raw_high is not None else 0.0,
                "raw_low": float(c.raw_low) if c.raw_low is not None else 0.0,
                "raw_close": float(c.raw_close) if c.raw_close is not None else 0.0,
                "raw_volume": float(c.raw_volume) if c.raw_volume is not None else 0.0,
                "extra_data": c.extra_data,
                "quarantine_reason": reason
            })
            
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise StorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        dialect_name = session.bind.dialect.name
        stmt = self._get_insert_stmt(
            dialect_name, 
            QuarantinedCandleOrm, 
            values, 
            ['provider', 'symbol_id', 'timeframe', 'raw_timestamp']
        )
        
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to batch insert quarantined candles: {e}")
            raise StorageException(f"Database error during quarantine batch insert: {e}")
