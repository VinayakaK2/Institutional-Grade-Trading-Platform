import logging
from datetime import datetime, timezone
from backend.liquidity_grab_engine.models.models import (
    LiquidityGrabExecutionContext,
    LiquidityGrabSnapshot,
    LiquidityGrabConfigurationReference
)
from backend.liquidity_grab_engine.pipeline.pipeline import LiquidityGrabPipeline
from backend.liquidity_grab_engine.contracts.repository import ILiquidityGrabRepository
from backend.liquidity_grab_engine.validation.structural import StructuralValidator
from backend.liquidity_grab_engine.validation.consistency import ConsistencyValidator

logger = logging.getLogger(__name__)

class LiquidityGrabEngine:
    """
    Orchestrates the execution of the Liquidity Grab Foundation.
    Validates inputs, constructs contexts, executes the pipeline, and saves snapshots.
    """
    
    def __init__(self, pipeline: LiquidityGrabPipeline, repository: ILiquidityGrabRepository):
        self.pipeline = pipeline
        self.repository = repository
        
    async def execute(self, context: LiquidityGrabExecutionContext) -> LiquidityGrabSnapshot:
        """
        Executes the liquidity grab generation process.
        """
        logger.info("LiquidityGrabEngine Execution Started.")
        
        # Log structured metadata
        logger.info(f"Pipeline Version: {context.metadata.pipeline_version}")
        logger.info(f"Configuration Hash: {context.configuration.generate_hash()}")
        logger.info(f"Dataset Version: {context.dataset_version}")
        logger.info(f"Parent Trend Snapshot Version: {context.parent_trend_snapshot_version}")
        logger.info(f"Parent Consolidation Snapshot Version: {context.parent_consolidation_snapshot_version}")
        
        # 1. Validation
        StructuralValidator.validate_context(context)
        ConsistencyValidator.validate_lineage(context)
        
        # 2. Build initial empty snapshot
        snapshot_id = LiquidityGrabSnapshot.generate_id(
            symbol_id=context.symbol.symbol,
            timeframe=context.timeframe.value,
            dataset_version=context.dataset_version,
            trend_version=context.parent_trend_snapshot_version,
            consolidation_version=context.parent_consolidation_snapshot_version
        )
        
        config_ref = LiquidityGrabConfigurationReference(
            version=context.configuration.version,
            config_hash=context.configuration.generate_hash()
        )
        
        initial_snapshot = LiquidityGrabSnapshot(
            snapshot_id=snapshot_id,
            symbol_id=context.symbol.symbol,
            timeframe=context.timeframe.value,
            snapshot_version=1,
            dataset_version=context.dataset_version,
            parent_trend_snapshot_version=context.parent_trend_snapshot_version,
            parent_consolidation_snapshot_version=context.parent_consolidation_snapshot_version,
            pipeline_version=context.metadata.pipeline_version,
            config_reference=config_ref,
            created_timestamp=datetime.now(timezone.utc),
            grabs=[]
        )
        
        # 3. Execute Pipeline
        final_snapshot = self.pipeline.execute(context, initial_snapshot)
        
        # 4. Save to Repository
        await self.repository.save(final_snapshot)
        
        logger.info("LiquidityGrabEngine Execution Finished.")
        return final_snapshot
