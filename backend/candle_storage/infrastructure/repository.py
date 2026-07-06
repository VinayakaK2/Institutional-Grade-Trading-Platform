"""
PostgreSQL Candle Repository
Generic idempotent batch operations for candle datasets.
"""
from typing import List, AsyncGenerator, Any, Optional
import logging
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from backend.application.uow.base import BaseUnitOfWork
from backend.candle_storage.contracts.repository import CandleRepositoryContract
from backend.candle_storage.models.dataset import CandleQueryFilters, DatasetType
from backend.candle_storage.exceptions import CandleStorageException
from backend.infrastructure.database.orm.candle import RawCandleOrm, CandleOrm, AdjustedCandleOrm
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle

logger = logging.getLogger(__name__)

class PostgreSQLCandleRepository(CandleRepositoryContract):
    def __init__(self, uow: BaseUnitOfWork):
        self._uow = uow
        
    def _get_orm_class(self, dataset_type: str):
        if dataset_type == DatasetType.RAW:
            return RawCandleOrm
        elif dataset_type == DatasetType.CANONICAL:
            return CandleOrm
        elif dataset_type == DatasetType.ADJUSTED:
            return AdjustedCandleOrm
        raise CandleStorageException(f"Unknown dataset_type: {dataset_type}")

    def _get_insert_stmt(self, dialect_name: str, table, values: list, index_elements: list) -> Any:
        if dialect_name == "sqlite":
            s_stmt = sqlite_insert(table).values(values)
            return s_stmt.on_conflict_do_nothing(index_elements=index_elements)
        else:
            p_stmt = pg_insert(table).values(values)
            return p_stmt.on_conflict_do_nothing(index_elements=index_elements)

    async def save_batch(self, dataset_type: str, dataset_version: Optional[str], candles: List[Any]) -> None:
        if not candles:
            return
            
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise CandleStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        dialect_name = session.bind.dialect.name
        orm_class = self._get_orm_class(dataset_type)
        
        values = []
        if dataset_type == DatasetType.RAW:
            index_elements = ['provider', 'symbol_id', 'timeframe', 'raw_timestamp']
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
        elif dataset_type == DatasetType.CANONICAL:
            index_elements = ['symbol_id', 'timeframe', 'timestamp']
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
        elif dataset_type == DatasetType.ADJUSTED:
            index_elements = ['dataset_version', 'symbol_id', 'timeframe', 'timestamp']
            for c in candles:
                values.append({
                    "dataset_version": dataset_version,
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
        else:
            raise CandleStorageException(f"Unsupported save for dataset_type: {dataset_type}")
            
        stmt = self._get_insert_stmt(dialect_name, orm_class, values, index_elements)
        
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to batch insert {dataset_type} candles: {e}")
            raise CandleStorageException(f"Database error during {dataset_type} batch insert: {e}")

    async def get_stream(self, filters: CandleQueryFilters) -> AsyncGenerator[Any, None]:
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise CandleStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        orm_class = self._get_orm_class(filters.dataset_type)
        
        stmt = select(orm_class).where(
            orm_class.symbol_id == filters.symbol.symbol,
            orm_class.timeframe == filters.timeframe.value
        )
        
        if filters.dataset_type == DatasetType.ADJUSTED:
            stmt = stmt.where(orm_class.dataset_version == filters.dataset_version)
            
        timestamp_col = orm_class.raw_timestamp if filters.dataset_type == DatasetType.RAW else orm_class.timestamp
            
        if filters.start_time:
            if filters.dataset_type == DatasetType.RAW:
                stmt = stmt.where(orm_class.raw_timestamp >= str(filters.start_time))
            else:
                stmt = stmt.where(orm_class.timestamp >= filters.start_time)
                
        if filters.end_time:
            if filters.dataset_type == DatasetType.RAW:
                stmt = stmt.where(orm_class.raw_timestamp <= str(filters.end_time))
            else:
                stmt = stmt.where(orm_class.timestamp <= filters.end_time)
                
        if filters.order_by_desc:
            stmt = stmt.order_by(timestamp_col.desc())
        else:
            stmt = stmt.order_by(timestamp_col.asc())
            
        if filters.limit:
            stmt = stmt.limit(filters.limit)
            
        # yield_per for memory efficiency with large result sets
        result = await session.stream(stmt)
        
        async for row in result.scalars():
            if filters.dataset_type == DatasetType.RAW:
                yield RawCandle(
                    provider=row.provider,
                    symbol=filters.symbol,
                    timeframe=filters.timeframe,
                    raw_timestamp=row.raw_timestamp,
                    raw_open=row.raw_open,
                    raw_high=row.raw_high,
                    raw_low=row.raw_low,
                    raw_close=row.raw_close,
                    raw_volume=row.raw_volume,
                    extra_data=row.extra_data
                )
            else:
                yield Candle(
                    symbol=filters.symbol,
                    timeframe=filters.timeframe,
                    timestamp=row.timestamp,
                    open=row.open,
                    high=row.high,
                    low=row.low,
                    close=row.close,
                    volume=row.volume,
                    is_completed=row.is_completed
                )

    async def delete_dataset(self, dataset_type: str, symbol_id: str, timeframe: str, dataset_version: Optional[str] = None) -> None:
        session: Any = getattr(self._uow, "_session", None)
        if not session:
            raise CandleStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        from sqlalchemy import delete
        orm_class = self._get_orm_class(dataset_type)
        
        stmt = delete(orm_class).where(
            orm_class.symbol_id == symbol_id,
            orm_class.timeframe == timeframe
        )
        
        if dataset_type == DatasetType.ADJUSTED:
            if not dataset_version:
                raise CandleStorageException("dataset_version is required when deleting ADJUSTED datasets.")
            stmt = stmt.where(orm_class.dataset_version == dataset_version)
            
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to delete {dataset_type} dataset: {e}")
            raise CandleStorageException(f"Database error during dataset deletion: {e}")
