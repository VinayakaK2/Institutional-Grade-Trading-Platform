from backend.trade_validation_engine.signal_aggregation.engine.engine import SignalAggregationEngine
from backend.trade_validation_engine.signal_aggregation.pipeline.pipeline import SignalAggregationPipeline
from backend.trade_validation_engine.signal_aggregation.repository.memory import InMemorySignalAggregationRepository
from backend.trade_validation_engine.signal_aggregation.query_service.memory import InMemorySignalAggregationQueryService
from backend.trade_validation_engine.signal_aggregation.stages.universe import UniverseAggregationStage, MockUniverseSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.watchlist import WatchlistAggregationStage, MockWatchlistSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.trend import TrendAggregationStage, MockTrendSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.consolidation import ConsolidationAggregationStage, MockConsolidationSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.liquidity_grab import LiquidityGrabAggregationStage, MockLiquidityGrabSnapshot
from backend.trade_validation_engine.signal_aggregation.stages.assembly import EvidenceAssemblyStage

from backend.trade_validation_engine.signal_aggregation.contracts.upstream import IReadOnlySnapshotQueryService
from typing import Optional, TypeVar

T = TypeVar('T')

class MockQueryService(IReadOnlySnapshotQueryService[T]):
    def __init__(self, mock_obj: T):
        self.mock_obj = mock_obj
    async def get_by_snapshot_version(self, symbol: str, timeframe: str, snapshot_version: int) -> Optional[T]:
        return self.mock_obj
    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[T]:
        return self.mock_obj

class SignalAggregationContainer:
    """
    Dependency Injection Container for the Signal Aggregation Engine.
    """
    def __init__(self):
        # Initialize storage
        self.repository = InMemorySignalAggregationRepository()
        self.query_service = InMemorySignalAggregationQueryService(self.repository._storage)

        # Initialize mock upstream services
        self.universe_qs = MockQueryService(MockUniverseSnapshot())
        self.watchlist_qs = MockQueryService(MockWatchlistSnapshot())
        self.trend_qs = MockQueryService(MockTrendSnapshot())
        self.consolidation_qs = MockQueryService(MockConsolidationSnapshot())
        self.liquidity_grab_qs = MockQueryService(MockLiquidityGrabSnapshot())

        # Initialize stages
        self.stages = [
            UniverseAggregationStage(self.universe_qs),
            WatchlistAggregationStage(self.watchlist_qs),
            TrendAggregationStage(self.trend_qs),
            ConsolidationAggregationStage(self.consolidation_qs),
            LiquidityGrabAggregationStage(self.liquidity_grab_qs),
            EvidenceAssemblyStage()
        ]

        # Initialize pipeline
        self.pipeline = SignalAggregationPipeline(self.stages)

        # Initialize engine
        self.engine = SignalAggregationEngine(
            pipeline=self.pipeline,
            repository=self.repository
        )
