import hashlib
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, AsyncGenerator

from backend.core.logger import get_logger
from backend.universe_engine.contracts.optimization import (
    IUniverseOptimizationRepository,
)
from backend.universe_engine.classification.models import ClassifiedUniverse, ClassifiedSymbol
from backend.universe_engine.optimization.models import (
    UniverseOptimizationConfiguration,
    UniverseOptimizationContext,
    OptimizedUniverse,
    UniverseOptimizationResult,
)
from backend.universe_engine.optimization.pipeline import UniverseOptimizationPipeline

logger = get_logger(__name__)

class UniverseOptimizationEngine:
    """
    Orchestrates the optimization of the Universe pipeline execution strategy.
    Does not modify business data. Instead, it computes diffs, batches, and executes
    work in parallel where necessary.
    """
    def __init__(
        self,
        config: UniverseOptimizationConfiguration,
        pipeline: UniverseOptimizationPipeline,
        repository: IUniverseOptimizationRepository,
        pipeline_version: str = "1.0.0"
    ):
        self._config = config
        self._pipeline = pipeline
        self._repository = repository
        self._pipeline_version = pipeline_version
        self._config_hash = self._hash_config()

    def _hash_config(self) -> str:
        config_json = self._config.model_dump_json()
        return hashlib.sha256(config_json.encode('utf-8')).hexdigest()

    async def _symbol_stream(self, universe: ClassifiedUniverse) -> AsyncGenerator[ClassifiedSymbol, None]:
        """Converts the in-memory list to an async stream for lazy evaluation downstream."""
        for symbol in universe.classified_symbols:
            yield symbol

    async def generate_optimized_universe(
        self, 
        run_id: str, 
        parent_classified_universe: ClassifiedUniverse,
        previous_optimized_universe: Optional[OptimizedUniverse] = None
    ) -> UniverseOptimizationResult:
        """
        Executes the optimization pipeline and persists the OptimizedUniverse metadata.
        """
        logger.info(f"Starting Optimization Engine [Run: {run_id}] | Parent Classified: {parent_classified_universe.classified_universe_id}")
        
        start_time = time.time()
        started_at = datetime.now(timezone.utc)
        
        prev_id = previous_optimized_universe.optimized_universe_id if previous_optimized_universe else None
        
        context = UniverseOptimizationContext(
            run_id=run_id,
            parent_classified_universe_id=parent_classified_universe.classified_universe_id,
            previous_optimized_universe_id=prev_id,
            config=self._config,
            started_at=started_at
        )

        prev_fingerprints = previous_optimized_universe.symbol_fingerprints if previous_optimized_universe else None

        # Create symbol stream
        symbol_stream = self._symbol_stream(parent_classified_universe)

        # Execute Pipeline (Lazy iteration)
        pipeline_stream = self._pipeline.execute(context, symbol_stream, prev_fingerprints)
        
        # We must consume the stream to drive the pipeline stages.
        # We'll also collect the new fingerprints.
        new_fingerprints = {}
        async for task in pipeline_stream:
            new_fingerprints[task.symbol.symbol.symbol.symbol] = task.fingerprint
            
        context.metrics.processing_time_ms = (time.time() - start_time) * 1000

        # Generate Immutable Output Metadata
        optimized_universe_id = str(uuid.uuid4())
        
        optimized_universe = OptimizedUniverse(
            optimized_universe_id=optimized_universe_id,
            parent_classified_universe_id=parent_classified_universe.classified_universe_id,
            previous_optimized_universe_id=prev_id,
            pipeline_version=self._pipeline_version,
            config_hash=self._config_hash,
            created_at=datetime.now(timezone.utc),
            configuration_snapshot=self._config,
            optimization_metrics=context.metrics,
            symbol_fingerprints=new_fingerprints
        )

        # Persist
        await self._repository.save_optimized_universe(optimized_universe)
        logger.info(f"Successfully generated and saved Optimized Universe metadata: {optimized_universe_id}")

        return UniverseOptimizationResult(universe=optimized_universe)
