import logging
from datetime import datetime, timezone
from backend.consolidation_engine.pipeline.pipeline import ConsolidationPipeline
from backend.consolidation_engine.models.models import (
    ConsolidationExecutionContext, 
    ConsolidationSnapshot, 
    ConsolidationMetadata
)
from backend.consolidation_engine.config.config import ConsolidationConfiguration
from backend.consolidation_engine.validation.validator import ConsolidationValidator
from backend.consolidation_engine.contracts.contracts import IConsolidationRepository
from backend.consolidation_engine.models.fingerprint import BusinessFingerprint

logger = logging.getLogger(__name__)

class ConsolidationEngineCore:
    """
    Core entry point for Phase 8 Consolidation processing.
    Orchestrates configuration, validation, context initialization, and pipeline execution.
    """
    def __init__(self, repository: IConsolidationRepository, pipeline: ConsolidationPipeline, config: ConsolidationConfiguration):
        self.repository = repository
        self.pipeline = pipeline
        self.config = config
        
    async def process(self, dataset_version: int, trend_snapshot_version: int, base_fingerprint: BusinessFingerprint) -> ConsolidationSnapshot:
        """
        Validates inputs, initializes context, runs the pipeline, and returns/saves the snapshot.
        """
        logger.info(f"ConsolidationEngineCore processing dataset v{dataset_version}, trend snapshot v{trend_snapshot_version}")
        
        # Validation
        ConsolidationValidator.validate_execution_context(dataset_version, trend_snapshot_version)
        ConsolidationValidator.validate_config(self.config)
        ConsolidationValidator.validate_trend_snapshot(trend_snapshot_version)
        
        # Context Initialization
        start_time = datetime.now(timezone.utc)
        
        metadata = ConsolidationMetadata(
            execution_start_timestamp=start_time,
            pipeline_version="1.0"
        )
        
        context = ConsolidationExecutionContext(
            dataset_version=dataset_version,
            trend_snapshot_version=trend_snapshot_version,
            configuration=self.config,
            metadata=metadata
        )
        
        # Determine snapshot version
        latest_snapshot = await self.repository.load_latest_snapshot()
        next_version = (latest_snapshot.snapshot_version + 1) if latest_snapshot else 1
        
        # Create initial empty snapshot
        initial_snapshot = ConsolidationSnapshot(
            snapshot_version=next_version,
            parent_dataset_version=dataset_version,
            parent_trend_snapshot_version=trend_snapshot_version,
            pipeline_version="1.0",
            engine_version="1.0",
            config_version=self.config.config_version,
            config_hash=self.config.compute_hash(),
            business_fingerprint=base_fingerprint.compute_hash(),
            fingerprint_algorithm_version=base_fingerprint.fingerprint_algorithm_version,
            candidates=[]
        )
        
        # Execute Pipeline
        final_snapshot = self.pipeline.execute(context, initial_snapshot)
        
        # Log completion
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Consolidation processing completed in {duration:.2f}s. Detected {len(final_snapshot.candidates)} candidates.")
        
        # Save snapshot
        await self.repository.save_snapshot(final_snapshot)
        return final_snapshot
