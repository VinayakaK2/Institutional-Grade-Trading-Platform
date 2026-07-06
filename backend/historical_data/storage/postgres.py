"""
PostgreSQL Storage Adapter for Historical Data
"""
from typing import List, Any, AsyncGenerator
from datetime import datetime
import logging
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from backend.historical_data.contracts.storage import HistoricalStorageContract
from backend.historical_data.models.raw import RawCandle
from backend.infrastructure.database.orm.candle import RawCandleOrm, CandleOrm
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.models.metadata import DownloadMetadata
from backend.application.uow.base import BaseUnitOfWork
from backend.historical_data.exceptions import StorageException

logger = logging.getLogger(__name__)

class PostgreSQLHistoricalStorage(HistoricalStorageContract):
    """
    Implements HistoricalStorageContract using PostgreSQL 'ON CONFLICT DO NOTHING'
    for robust idempotent batch processing. Supports SQLite gracefully for testing.
    """
    def __init__(self, uow: BaseUnitOfWork):
        self._uow = uow
        
    def _get_insert_stmt(self, dialect_name: str, table, values: list, index_elements: list) -> Any:
        if dialect_name == "sqlite":
            s_stmt = sqlite_insert(table).values(values)
            return s_stmt.on_conflict_do_nothing(index_elements=index_elements)
        else:
            # Default to postgres
            p_stmt = pg_insert(table).values(values)
            return p_stmt.on_conflict_do_nothing(index_elements=index_elements)

    async def save_raw_candles(self, candles: List[RawCandle]) -> None:
        if not candles:
            return
            
        values = []
        for c in candles:
            values.append({
                "provider": c.provider,
                "symbol_id": c.symbol.symbol,
                "timeframe": c.timeframe.value,
                "raw_timestamp": str(c.raw_timestamp),
                "raw_open": float(c.raw_open),
                "raw_high": float(c.raw_high),
                "raw_low": float(c.raw_low),
                "raw_close": float(c.raw_close),
                "raw_volume": float(c.raw_volume),
                "extra_data": c.extra_data
            })
            
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise StorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        dialect_name = session.bind.dialect.name
        stmt = self._get_insert_stmt(
            dialect_name, 
            RawCandleOrm, 
            values, 
            ['provider', 'symbol_id', 'timeframe', 'raw_timestamp']
        )
        
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to batch insert raw candles: {e}")
            raise StorageException(f"Database error during raw batch insert: {e}")

    async def save_normalized_candles(self, candles: List[Candle]) -> None:
        if not candles:
            return
            
        values = []
        for c in candles:
            values.append({
                "symbol_id": c.symbol.symbol,
                "timeframe": c.timeframe.value,
                "timestamp": c.timestamp,
                "open": float(c.open),
                "high": float(c.high),
                "low": float(c.low),
                "close": float(c.close),
                "volume": float(c.volume),
                "is_completed": c.is_completed
            })
            
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise StorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        dialect_name = session.bind.dialect.name
        stmt = self._get_insert_stmt(
            dialect_name, 
            CandleOrm, 
            values, 
            ['symbol_id', 'timeframe', 'timestamp']
        )
        
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to batch insert normalized candles: {e}")
            raise StorageException(f"Database error during normalized batch insert: {e}")
            
    async def get_raw_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> AsyncGenerator[RawCandle, None]:
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise StorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        from sqlalchemy import select
        stmt = select(RawCandleOrm).where(
            RawCandleOrm.symbol_id == symbol.symbol,
            RawCandleOrm.timeframe == timeframe.value
        ).order_by(RawCandleOrm.raw_timestamp)
        
        result = await session.execute(stmt)
        for row in result.scalars():
            yield RawCandle(
                provider=row.provider,
                symbol=symbol,
                timeframe=timeframe,
                raw_timestamp=row.raw_timestamp,
                raw_open=row.raw_open,
                raw_high=row.raw_high,
                raw_low=row.raw_low,
                raw_close=row.raw_close,
                raw_volume=row.raw_volume,
                extra_data=row.extra_data
            )
            
    async def save_metadata(self, metadata: DownloadMetadata) -> None:
        from backend.historical_data.orm.models import DownloadMetadataOrm
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise StorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        values = {
            "request_id": metadata.request_id,
            "symbol_id": metadata.symbol.symbol,
            "timeframe": metadata.timeframe.value,
            "provider": metadata.provider,
            "start_date": metadata.start_date,
            "end_date": metadata.end_date,
            "status": metadata.status.value,
            "records_downloaded": metadata.records_downloaded,
            "records_saved": metadata.records_saved,
            "failure_reason": metadata.failure_reason,
            "download_duration_ms": metadata.download_duration_ms or 0
        }
        
        dialect_name = session.bind.dialect.name
        if dialect_name == "sqlite":
            stmt = sqlite_insert(DownloadMetadataOrm).values(values)
            # DO UPDATE SET status=EXCLUDED.status etc. to mimic upsert idempotency
            update_dict = {k: v for k, v in values.items() if k != "request_id"}
            stmt = stmt.on_conflict_do_update(
                index_elements=['request_id'],
                set_=update_dict
            )
        else:
            stmt = pg_insert(DownloadMetadataOrm).values(values)
            update_dict = {k: v for k, v in values.items() if k != "request_id"}
            stmt = stmt.on_conflict_do_update(
                index_elements=['request_id'],
                set_=update_dict
            )
            
        try:
            await session.execute(stmt)
            await session.commit() # ensure the metadata state writes immediately
        except Exception as e:
            logger.error(f"Failed to upsert download metadata: {e}")
            raise StorageException(f"Database error during metadata upsert: {e}")
