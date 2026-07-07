import hashlib
import uuid
from datetime import datetime, timezone

from backend.universe_engine.contracts.data_quality import (
    IDataQualityDataProvider,
    IMarketCalendarProvider,
    ICorporateActionProvider,
    IDataQualityRepository,
)
from backend.universe_engine.data_quality.pipeline import DataQualityFilterPipeline
from backend.universe_engine.data_quality.models import (
    DataQualityFilterConfiguration,
    DataQualityFilterContext,
    CertifiedUniverse,
)
from backend.universe_engine.liquidity.models import LiquidityQualifiedUniverse
from backend.core.logger import get_logger

logger = get_logger(__name__)


class DataQualityFilterResult:
    def __init__(self, certified_universe: CertifiedUniverse):
        self.universe = certified_universe


class DataQualityFilterEngine:
    """
    Orchestrates the data quality filtering pipeline.
    
    PROVIDER UNAVAILABILITY BEHAVIOUR:
    If a provider (e.g. IDataQualityDataProvider) is temporarily unavailable or returns an unexpected
    infrastructure error, the pipeline should NOT silently reject the symbol. 
    Instead, infrastructure failures must be allowed to propagate (or be wrapped in an explicit
    InfrastructureError) so that the entire pipeline run fails. This prevents temporary outages from 
    producing incorrect certification results.
    """
    def __init__(
        self,
        config: DataQualityFilterConfiguration,
        pipeline: DataQualityFilterPipeline,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
        repository: IDataQualityRepository,
        pipeline_version: str = "1.0.0",
    ):
        self.config = config
        self.pipeline = pipeline
        self.data_provider = data_provider
        self.calendar_provider = calendar_provider
        self.corporate_action_provider = corporate_action_provider
        self.repository = repository
        self.pipeline_version = pipeline_version
        self._config_hash = self._hash_config()

    def _hash_config(self) -> str:
        config_json = self.config.model_dump_json(exclude_none=True)
        return hashlib.sha256(config_json.encode("utf-8")).hexdigest()

    async def generate_certified_universe(
        self, run_id: str, parent_universe: LiquidityQualifiedUniverse
    ) -> DataQualityFilterResult:
        logger.info(
            f"Starting Data Quality Engine [Run: {run_id}] | Parent Universe: {parent_universe.liquidity_universe_id}"
        )

        # We start with the qualified symbols from the Liquidity phase
        initial_instruments = parent_universe.qualified_symbols

        context = DataQualityFilterContext(
            run_id=run_id,
            parent_snapshot_id=parent_universe.liquidity_universe_id,
            config=self.config,
            certified_instruments=initial_instruments.copy(),
            started_at=datetime.now(timezone.utc),
        )
        context.statistics.initial_instrument_count = len(initial_instruments)
        context.statistics.pipeline_version = self.pipeline_version

        # Execute Pipeline
        context = await self.pipeline.execute(
            context,
            self.data_provider,
            self.calendar_provider,
            self.corporate_action_provider,
        )

        context.statistics.final_certified_count = len(context.certified_instruments)

        # Determine dataset version from the first certified instrument or "UNKNOWN"
        dataset_version = "UNKNOWN"
        if context.certified_instruments:
            dataset_version = await self.data_provider.get_dataset_version(
                context.certified_instruments[0]
            )

        certified_universe_id = str(uuid.uuid4())

        certified_universe = CertifiedUniverse(
            certified_universe_id=certified_universe_id,
            parent_snapshot_id=parent_universe.liquidity_universe_id,
            pipeline_version=self.pipeline_version,
            config_hash=self._config_hash,
            dataset_version=dataset_version,
            created_at=datetime.now(timezone.utc),
            certified_symbols=context.certified_instruments,
            rejected_symbols=context.rejected_details,
            configuration_snapshot=self.config,
            statistics=context.statistics,
        )

        await self.repository.save_certified_universe(certified_universe)

        logger.info(
            f"Successfully generated and saved Certified Universe: {certified_universe_id}"
        )
        return DataQualityFilterResult(certified_universe=certified_universe)
