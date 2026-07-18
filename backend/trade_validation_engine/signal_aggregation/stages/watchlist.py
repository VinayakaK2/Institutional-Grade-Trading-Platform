import time
from typing import Dict, Any

from backend.trade_validation_engine.signal_aggregation.stages.base import IAggregationStage
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult
from backend.trade_validation_engine.signal_aggregation.contracts.upstream import IReadOnlySnapshotQueryService
from backend.trade_validation_engine.signal_aggregation.models.evidence import WatchlistEvidence
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import SnapshotNotFoundError

class MockWatchlistSnapshot:
    def __init__(self):
        self.dataset_version = 1
        self.configuration_hash = "mock_hash"
        self.algorithm_version = "v1"
        self.state = "WATCHED"
        self.score = 0.85

class WatchlistAggregationStage(IAggregationStage):
    """
    Loads the Watchlist snapshot and constructs WatchlistEvidence.
    """
    def __init__(self, query_service: IReadOnlySnapshotQueryService[MockWatchlistSnapshot]):
        self._query_service = query_service

    @property
    def stage_id(self) -> str:
        return "WatchlistAggregationStage"

    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        start_time = time.monotonic()
        try:
            snapshot = await self._query_service.get_by_snapshot_version(
                symbol=request.symbol,
                timeframe=request.timeframe,
                snapshot_version=request.watchlist_snapshot_version
            )
            
            if not snapshot:
                raise SnapshotNotFoundError(f"Watchlist snapshot {request.watchlist_snapshot_version} not found.")

            evidence = WatchlistEvidence(
                snapshot_version=request.watchlist_snapshot_version,
                dataset_version=snapshot.dataset_version,
                configuration_hash=snapshot.configuration_hash,
                algorithm_version=snapshot.algorithm_version,
                watchlist_state=snapshot.state,
                watchlist_score=snapshot.score,
                metadata={}
            )

            duration = int((time.monotonic() - start_time) * 1000)
            return AggregationStageResult(
                stage_id=self.stage_id,
                success=True,
                evidence=evidence,
                duration_ms=duration
            )

        except Exception as e:
            duration = int((time.monotonic() - start_time) * 1000)
            return AggregationStageResult(
                stage_id=self.stage_id,
                success=False,
                error_message=str(e),
                duration_ms=duration
            )
