"""
Implementations of the Candidate Universe Query Service.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from backend.universe_engine.contracts.query import ICandidateUniverseQueryService
from backend.universe_engine.models.read_views import CandidateUniverseView, CandidateUniverseSymbol
from backend.infrastructure.database.orm.classification import ClassifiedUniverseModel
from backend.infrastructure.database.orm.universe import UniverseSnapshotModel
from backend.universe_engine.models.universe import TradingStatus
from backend.universe_engine.classification.models import DataQualityClassification
from backend.market_data.models.symbol import SymbolReference, ExchangeReference


class PostgreSQLCandidateUniverseQueryService(ICandidateUniverseQueryService):
    """
    SQLAlchemy implementation of the query service.
    Reads from the ClassifiedUniverse read-model projection.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def load_latest(self) -> Optional[CandidateUniverseView]:
        async with self._session_factory() as session:
            # Get latest ClassifiedUniverse
            stmt = select(ClassifiedUniverseModel).order_by(desc(ClassifiedUniverseModel.created_at)).limit(1)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                return None
                
            # We need the parent universe snapshot to get the version
            parent_stmt = select(UniverseSnapshotModel).where(
                UniverseSnapshotModel.snapshot_id == model.parent_certified_universe_id
            )
            parent_result = await session.execute(parent_stmt)
            parent_model = parent_result.scalar_one_or_none()
            universe_version = parent_model.version if parent_model else 0

            return self._map_to_view(model, universe_version)

    async def load_by_version(self, version: int) -> Optional[CandidateUniverseView]:
        async with self._session_factory() as session:
            # 1. Find the parent universe snapshot ID by version
            parent_stmt = select(UniverseSnapshotModel).where(
                UniverseSnapshotModel.version == version
            )
            parent_result = await session.execute(parent_stmt)
            parent_model = parent_result.scalar_one_or_none()
            
            if not parent_model:
                return None
                
            # 2. Find the classified universe corresponding to this parent
            stmt = select(ClassifiedUniverseModel).where(
                ClassifiedUniverseModel.parent_certified_universe_id == parent_model.snapshot_id
            ).order_by(desc(ClassifiedUniverseModel.created_at)).limit(1)
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return None

            return self._map_to_view(model, version)

    def _map_to_view(self, model: ClassifiedUniverseModel, universe_version: int) -> CandidateUniverseView:
        symbols = []
        for symbol_dict in model.classified_symbols:
            # symbol_dict is a serialized ClassifiedSymbol
            u_inst = symbol_dict.get("symbol", {})
            sym_ref = u_inst.get("symbol", {})
            ex_ref = sym_ref.get("exchange", {})
            
            symbols.append(
                CandidateUniverseSymbol(
                    symbol=SymbolReference(
                        symbol=sym_ref.get("symbol", ""),
                        exchange=ExchangeReference(code=ex_ref.get("code", ""))
                    ),
                    exchange=ex_ref.get("code", ""),
                    instrument_type=u_inst.get("instrument_type", "UNKNOWN"),
                    is_active=u_inst.get("trading_status") == TradingStatus.ACTIVE.value,
                    is_certified=symbol_dict.get("data_quality") == DataQualityClassification.CERTIFIED.value
                )
            )

        return CandidateUniverseView(
            universe_snapshot_id=model.parent_certified_universe_id,
            universe_version=universe_version,
            pipeline_version=model.pipeline_version,
            created_at=model.created_at,
            symbols=symbols
        )


class InMemoryCandidateUniverseQueryService(ICandidateUniverseQueryService):
    """
    In-memory mock for testing.
    """
    def __init__(self):
        self._views = []

    def add_view(self, view: CandidateUniverseView):
        self._views.append(view)

    async def load_latest(self) -> Optional[CandidateUniverseView]:
        if not self._views:
            return None
        return max(self._views, key=lambda v: v.created_at)

    async def load_by_version(self, version: int) -> Optional[CandidateUniverseView]:
        for view in self._views:
            if view.universe_version == version:
                return view
        return None
