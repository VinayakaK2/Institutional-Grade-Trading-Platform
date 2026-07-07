import hashlib
import uuid
import time
from datetime import datetime, timezone

from backend.core.logger import get_logger
from backend.universe_engine.contracts.classification import (
    IClassificationDataProvider,
    IUniverseClassificationRepository,
)
from backend.universe_engine.classification.models import (
    UniverseClassificationConfiguration,
    UniverseClassificationContext,
    ClassifiedUniverse,
    ClassifiedSymbol,
    UniverseClassificationResult,
)
from backend.universe_engine.classification.pipeline import UniverseClassificationPipeline
from backend.universe_engine.data_quality.models import CertifiedUniverse

logger = get_logger(__name__)

class UniverseClassificationEngine:
    """
    Orchestrates the classification process, classifying structural instruments
    by mapping them to configured buckets (Market Cap, Sector, Industry, etc).
    """
    def __init__(
        self,
        config: UniverseClassificationConfiguration,
        pipeline: UniverseClassificationPipeline,
        data_provider: IClassificationDataProvider,
        repository: IUniverseClassificationRepository,
        pipeline_version: str = "1.0.0"
    ):
        self._config = config
        self._pipeline = pipeline
        self._data_provider = data_provider
        self._repository = repository
        self._pipeline_version = pipeline_version
        self._config_hash = self._hash_config()

    def _hash_config(self) -> str:
        config_json = self._config.model_dump_json()
        return hashlib.sha256(config_json.encode('utf-8')).hexdigest()

    async def generate_classified_universe(
        self, 
        run_id: str, 
        parent_certified_universe: CertifiedUniverse,
        parent_liquidity_metrics: dict
    ) -> UniverseClassificationResult:
        """
        Executes the classification pipeline and persists the ClassifiedUniverse.
        """
        logger.info(f"Starting Classification Engine [Run: {run_id}] | Parent Certified: {parent_certified_universe.certified_universe_id}")
        
        start_time = time.time()
        started_at = datetime.now(timezone.utc)
        
        # Initialize classified symbols with base UniverseInstrument
        initial_classified_symbols = {
            instr.symbol.symbol: ClassifiedSymbol(symbol=instr)
            for instr in parent_certified_universe.certified_symbols
        }

        context = UniverseClassificationContext(
            run_id=run_id,
            parent_certified_universe_id=parent_certified_universe.certified_universe_id,
            config=self._config,
            classified_symbols=initial_classified_symbols,
            parent_liquidity_metrics=parent_liquidity_metrics,
            started_at=started_at
        )
        context.statistics.total_symbols = len(context.classified_symbols)
        context.statistics.pipeline_version = self._pipeline_version

        # Execute Pipeline
        context = await self._pipeline.execute(context, self._data_provider)
        
        context.statistics.processing_time_ms = (time.time() - start_time) * 1000

        # Generate Immutable Output
        classified_universe_id = str(uuid.uuid4())
        
        classified_universe = ClassifiedUniverse(
            classified_universe_id=classified_universe_id,
            parent_certified_universe_id=parent_certified_universe.certified_universe_id,
            pipeline_version=self._pipeline_version,
            config_hash=self._config_hash,
            created_at=datetime.now(timezone.utc),
            classified_symbols=list(context.classified_symbols.values()),
            configuration_snapshot=self._config,
            statistics=context.statistics
        )

        # Persist
        await self._repository.save_classified_universe(classified_universe)
        logger.info(f"Successfully generated and saved Classified Universe: {classified_universe_id}")

        return UniverseClassificationResult(universe=classified_universe)
