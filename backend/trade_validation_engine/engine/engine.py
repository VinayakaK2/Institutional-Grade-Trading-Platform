import time
import logging
from backend.trade_validation_engine.models.models import TradeValidationRequest, TradeValidationSnapshot, TradeValidationMetadata
from backend.trade_validation_engine.pipeline.pipeline import TradeValidationPipeline
from backend.trade_validation_engine.contracts.repository import ITradeValidationRepository
from backend.trade_validation_engine.validation.structural import TradeValidationStructuralValidator
from backend.trade_validation_engine.validation.consistency import TradeValidationConsistencyValidator
from backend.trade_validation_engine.exceptions.exceptions import TradeValidationError

logger = logging.getLogger(__name__)

class TradeValidationEngine:
    """
    Stateless orchestrator for the Trade Validation Engine.
    Coordinates validation, pipeline execution, and repository persistence.
    Does not contain or enforce any business logic.
    """
    
    def __init__(self, pipeline: TradeValidationPipeline, repository: ITradeValidationRepository):
        self.pipeline = pipeline
        self.repository = repository
        
    async def execute(self, request: TradeValidationRequest) -> TradeValidationSnapshot:
        """
        Executes the full trade validation lifecycle.
        """
        logger.info(f"TradeValidationEngine started for request {request.request_id}")
        start_time = time.time()
        
        try:
            # 1. Base Context Validation
            TradeValidationStructuralValidator.validate(request.context)
            TradeValidationConsistencyValidator.validate(request.context)
            
            # 2. Pipeline Execution
            pipeline_result = self.pipeline.execute(request.context)
            
            # 3. Snapshot Assembly
            snapshot_id = TradeValidationSnapshot.generate_id(
                symbol=request.context.symbol,
                timeframe=request.context.timeframe,
                dataset_version=request.context.dataset_version,
                wl_version=request.context.parent_watchlist_snapshot_version,
                t_version=request.context.parent_trend_snapshot_version,
                c_version=request.context.parent_consolidation_snapshot_version,
                lg_version=request.context.parent_liquidity_grab_snapshot_version
            )
            
            execution_duration = int((time.time() - start_time) * 1000)
            
            metadata = TradeValidationMetadata(
                execution_duration_ms=execution_duration
            )
            
            snapshot = TradeValidationSnapshot(
                snapshot_id=snapshot_id,
                symbol=request.context.symbol,
                timeframe=request.context.timeframe,
                pipeline_result=pipeline_result,
                context=request.context,
                metadata=metadata
            )
            
            # 4. Persistence
            await self.repository.save(snapshot)
            logger.info(f"Persisted validation snapshot {snapshot_id}")
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Trade Validation Engine failed: {str(e)}")
            if isinstance(e, TradeValidationError):
                raise
            raise TradeValidationError(f"Unexpected error in Trade Validation Engine: {str(e)}") from e
        finally:
            logger.info(f"TradeValidationEngine finished for request {request.request_id}")
