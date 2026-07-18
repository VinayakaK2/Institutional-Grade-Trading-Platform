import time
import logging

from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, SignalAggregationSnapshot, SignalAggregationMetadata
from backend.trade_validation_engine.signal_aggregation.pipeline.pipeline import SignalAggregationPipeline
from backend.trade_validation_engine.signal_aggregation.contracts.repository import ISignalAggregationRepository
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import InvalidAggregationRequestError

logger = logging.getLogger(__name__)

class SignalAggregationEngine:
    """
    Stateless orchestrator for the Signal Aggregation Phase.
    """
    def __init__(self, pipeline: SignalAggregationPipeline, repository: ISignalAggregationRepository):
        self._pipeline = pipeline
        self._repository = repository

    def _validate_request(self, request: SignalAggregationRequest) -> None:
        if not request.symbol or not request.timeframe:
            raise InvalidAggregationRequestError("Symbol and timeframe must be provided.")
        if request.dataset_version <= 0:
            raise InvalidAggregationRequestError("Dataset version must be positive.")
        if request.universe_snapshot_version <= 0:
            raise InvalidAggregationRequestError("Universe snapshot version must be positive.")
        if request.watchlist_snapshot_version <= 0:
            raise InvalidAggregationRequestError("Watchlist snapshot version must be positive.")
        if request.trend_snapshot_version <= 0:
            raise InvalidAggregationRequestError("Trend snapshot version must be positive.")
        if request.consolidation_snapshot_version <= 0:
            raise InvalidAggregationRequestError("Consolidation snapshot version must be positive.")
        if request.liquidity_grab_snapshot_version <= 0:
            raise InvalidAggregationRequestError("Liquidity Grab snapshot version must be positive.")

    async def execute(self, request: SignalAggregationRequest) -> SignalAggregationSnapshot:
        start_time = time.monotonic()
        
        # 1. Structural validation of the request
        self._validate_request(request)

        # 2. Execute the aggregation pipeline
        success, stage_results = await self._pipeline.execute(request)
        
        # 3. Extract the final assembled evidence from the assembly stage (last stage)
        assembled_evidence = None
        if success and stage_results:
            assembly_result = stage_results[-1]
            if assembly_result.success:
                assembled_evidence = assembly_result.evidence

        duration = int((time.monotonic() - start_time) * 1000)
        config_hash_str = str(abs(hash(str(request.configuration.model_dump()))))
        
        # 4. Generate deterministic ID
        aggregation_id = SignalAggregationSnapshot.generate_id(
            symbol=request.symbol,
            dataset_version=request.dataset_version,
            wl_version=request.watchlist_snapshot_version,
            t_version=request.trend_snapshot_version,
            c_version=request.consolidation_snapshot_version,
            lg_version=request.liquidity_grab_snapshot_version,
            config_hash=config_hash_str
        )

        # 5. Build the immutable snapshot
        snapshot = SignalAggregationSnapshot(
            aggregation_id=aggregation_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            success=success,
            stage_results=stage_results,
            aggregated_evidence=assembled_evidence,
            metadata=SignalAggregationMetadata(execution_duration_ms=duration)
        )

        # 6. Persist to repository
        # If it already exists, the repository will raise RepositoryError protecting immutability
        await self._repository.save(snapshot)

        return snapshot
