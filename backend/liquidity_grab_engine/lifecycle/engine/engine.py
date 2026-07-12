import logging
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot
from backend.liquidity_grab_engine.lifecycle.pipeline.pipeline import LiquidityGrabLifecyclePipeline
from backend.liquidity_grab_engine.lifecycle.contracts.repository import ILiquidityGrabLifecycleRepository
from backend.liquidity_grab_engine.lifecycle.validation.structural import LifecycleStructuralValidator
from backend.liquidity_grab_engine.lifecycle.validation.consistency import LifecycleConsistencyValidator

logger = logging.getLogger(__name__)

class LiquidityGrabLifecycleEngine:
    def __init__(
        self,
        pipeline: LiquidityGrabLifecyclePipeline,
        repository: ILiquidityGrabLifecycleRepository,
        structural_validator: LifecycleStructuralValidator,
        consistency_validator: LifecycleConsistencyValidator
    ) -> None:
        self._pipeline = pipeline
        self._repository = repository
        self._structural_validator = structural_validator
        self._consistency_validator = consistency_validator

    async def execute(self, context: LiquidityGrabLifecycleContext) -> LiquidityGrabLifecycleSnapshot:
        logger.info(f"Executing LifecycleEngine for candidate {context.candidate.candidate_id}")
        
        self._structural_validator.validate(context)
        self._consistency_validator.validate(context)
        
        snapshot = self._pipeline.execute(context)
        
        await self._repository.save(snapshot)
        logger.info(f"Lifecycle Engine completed. Snapshot saved: {snapshot.snapshot_id}")
        return snapshot
