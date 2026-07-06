import logging
from typing import List, AsyncGenerator
from sqlalchemy import select, desc, asc
from backend.application.uow.base import BaseUnitOfWork as UnitOfWorkContract
from backend.indicator_engine.contracts.repository import IndicatorRepositoryContract
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorQueryFilters, IndicatorType
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.infrastructure.database.orm.indicator import IndicatorOrm
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

logger = logging.getLogger(__name__)

class IndicatorStorageException(Exception):
    pass

class PostgreSQLIndicatorRepository(IndicatorRepositoryContract):
    def __init__(self, uow: UnitOfWorkContract):
        self._uow = uow

    def _get_insert_stmt(self, dialect_name: str, values: list, index_elements: list):
        if dialect_name == "sqlite":
            s_stmt = sqlite_insert(IndicatorOrm).values(values)
            return s_stmt.on_conflict_do_nothing(index_elements=index_elements)
        else:
            p_stmt = pg_insert(IndicatorOrm).values(values)
            return p_stmt.on_conflict_do_nothing(index_elements=index_elements)

    async def save_batch(self, indicators: List[IndicatorResult]) -> None:
        if not indicators:
            return
            
        session = getattr(self._uow, "_session", None)
        if not session:
            raise IndicatorStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        dialect_name = session.bind.dialect.name
        
        values = []
        index_elements = ['symbol_id', 'timeframe', 'dataset_version', 'timestamp', 'indicator_type', 'param_key']
        
        for ind in indicators:
            values.append({
                "symbol_id": ind.symbol.symbol,
                "timeframe": ind.timeframe.value,
                "dataset_version": ind.dataset_version,
                "timestamp": str(ind.timestamp),
                "indicator_type": ind.indicator_type.value,
                "param_key": ind.get_param_key(),
                "parameters": ind.parameters,
                "value": ind.value,
                "internal_state": ind.internal_state
            })
            
        stmt = self._get_insert_stmt(dialect_name, values, index_elements)
        try:
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to batch insert indicators: {e}")
            raise IndicatorStorageException(f"Database error during indicator batch insert: {e}")

    async def get_stream(self, filters: IndicatorQueryFilters) -> AsyncGenerator[IndicatorResult, None]:
        session = getattr(self._uow, "_session", None)
        if not session:
            raise IndicatorStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        stmt = select(IndicatorOrm).where(
            IndicatorOrm.symbol_id == filters.symbol.symbol,
            IndicatorOrm.timeframe == filters.timeframe.value,
            IndicatorOrm.dataset_version == filters.dataset_version,
            IndicatorOrm.indicator_type == filters.indicator_type.value,
            IndicatorOrm.param_key == filters.get_param_key()
        )
        
        if filters.start_time:
            stmt = stmt.where(IndicatorOrm.timestamp >= str(filters.start_time))
        if filters.end_time:
            stmt = stmt.where(IndicatorOrm.timestamp <= str(filters.end_time))
            
        stmt = stmt.order_by(asc(IndicatorOrm.timestamp))
        if filters.limit:
            stmt = stmt.limit(filters.limit)
            
        result = await session.execute(stmt)
        for row in result.scalars():
            from dateutil import parser
            dt = parser.parse(row.timestamp)
            yield IndicatorResult(
                symbol=SymbolReference(symbol=row.symbol_id, exchange=filters.symbol.exchange),
                timeframe=Timeframe(row.timeframe),
                dataset_version=row.dataset_version,
                timestamp=dt,
                indicator_type=IndicatorType(row.indicator_type),
                parameters=row.parameters,
                value=row.value,
                internal_state=row.internal_state
            )

    async def get_latest_timestamp(self, filters: IndicatorQueryFilters) -> str:
        session = getattr(self._uow, "_session", None)
        if not session:
            raise IndicatorStorageException("The provided UnitOfWork does not expose a SQLAlchemy session.")
            
        stmt = select(IndicatorOrm.timestamp).where(
            IndicatorOrm.symbol_id == filters.symbol.symbol,
            IndicatorOrm.timeframe == filters.timeframe.value,
            IndicatorOrm.dataset_version == filters.dataset_version,
            IndicatorOrm.indicator_type == filters.indicator_type.value,
            IndicatorOrm.param_key == filters.get_param_key()
        ).order_by(desc(IndicatorOrm.timestamp)).limit(1)
        
        result = await session.execute(stmt)
        val = result.scalar()
        return val if val else ""
