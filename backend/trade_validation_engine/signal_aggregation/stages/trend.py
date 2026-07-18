import time
from typing import Dict, Any

from backend.trade_validation_engine.signal_aggregation.stages.base import IAggregationStage
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult
from backend.trade_validation_engine.signal_aggregation.contracts.upstream import IReadOnlySnapshotQueryService
from backend.trade_validation_engine.signal_aggregation.models.evidence import TrendEvidence
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import SnapshotNotFoundError

class MockTrendSnapshot:
    def __init__(self):
        self.dataset_version = 1
        self.configuration_hash = "mock_hash"
        self.algorithm_version = "v1"
        self.state = "UPTREND"
        self.quality = 0.95

class TrendAggregationStage(IAggregationStage):
    """
    Loads the Trend snapshot and constructs TrendEvidence.
    """
    def __init__(self, query_service: IReadOnlySnapshotQueryService[MockTrendSnapshot]):
        self._query_service = query_service

    @property
    def stage_id(self) -> str:
        return "TrendAggregationStage"

    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        start_time = time.monotonic()
        try:
            snapshot = await self._query_service.get_by_snapshot_version(
                symbol=request.symbol,
                timeframe=request.timeframe,
                snapshot_version=request.trend_snapshot_version
            )
            
            if not snapshot:
                raise SnapshotNotFoundError(f"Trend snapshot {request.trend_snapshot_version} not found.")

            evidence = TrendEvidence(
                snapshot_version=request.trend_snapshot_version,
                dataset_version=snapshot.dataset_version,
                configuration_hash=snapshot.configuration_hash,
                algorithm_version=snapshot.algorithm_version,
                trend_state=snapshot.state,
                trend_quality=snapshot.quality,
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
