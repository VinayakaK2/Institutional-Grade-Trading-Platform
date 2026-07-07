import hashlib
import uuid
from datetime import datetime, timezone

from backend.core.logger import get_logger
from backend.universe_engine.models.universe import UniverseSnapshot
from backend.universe_engine.contracts.liquidity import (
    ILiquidityDataProvider,
    IFundamentalDataProvider,
    ILiquidityRepository
)
from backend.universe_engine.liquidity.models import (
    LiquidityFilterConfiguration,
    LiquidityFilterContext,
    LiquidityQualifiedUniverse,
    LiquidityFilterResult
)
from backend.universe_engine.liquidity.pipeline import LiquidityFilterPipeline

logger = get_logger(__name__)

class LiquidityFilterEngine:
    """
    Orchestrates the liquidity filtering process.
    Takes a structurally qualified UniverseSnapshot and applies the 
    LiquidityFilterPipeline to produce a LiquidityQualifiedUniverse.
    """
    def __init__(
        self,
        config: LiquidityFilterConfiguration,
        pipeline: LiquidityFilterPipeline,
        data_provider: ILiquidityDataProvider,
        fundamental_provider: IFundamentalDataProvider,
        repository: ILiquidityRepository,
        pipeline_version: str = "1.0.0"
    ):
        self._config = config
        self._pipeline = pipeline
        self._data_provider = data_provider
        self._fundamental_provider = fundamental_provider
        self._repository = repository
        self._pipeline_version = pipeline_version

    def _hash_config(self) -> str:
        """Deterministically hashes the current configuration."""
        config_json = self._config.model_dump_json(exclude_unset=True)
        return hashlib.sha256(config_json.encode('utf-8')).hexdigest()

    async def generate_liquidity_universe(self, run_id: str, parent_snapshot: UniverseSnapshot) -> LiquidityFilterResult:
        """
        Executes the liquidity pipeline and persists the qualified universe.
        """
        logger.info(f"Starting Liquidity Engine [Run: {run_id}] | Parent Snapshot: {parent_snapshot.snapshot_id}")

        started_at = datetime.now(timezone.utc)
        initial_count = len(parent_snapshot.instruments)

        # Initialize Context
        context = LiquidityFilterContext(
            run_id=run_id,
            parent_snapshot_id=parent_snapshot.snapshot_id,
            config=self._config,
            qualified_instruments=parent_snapshot.instruments.copy(),
            started_at=started_at
        )
        context.statistics.initial_instrument_count = initial_count
        context.statistics.pipeline_version = self._pipeline_version

        # Execute Pipeline
        context = await self._pipeline.execute(
            context=context,
            data_provider=self._data_provider,
            fundamental_provider=self._fundamental_provider
        )

        # Finalize Statistics
        context.statistics.final_qualified_count = len(context.qualified_instruments)

        # Generate Immutable Output
        liquidity_universe_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        qualified_universe = LiquidityQualifiedUniverse(
            liquidity_universe_id=liquidity_universe_id,
            parent_snapshot_id=parent_snapshot.snapshot_id,
            pipeline_version=self._pipeline_version,
            config_hash=self._hash_config(),
            created_at=created_at,
            qualified_symbols=context.qualified_instruments,
            rejected_symbols=context.rejected_details,
            configuration_snapshot=self._config,
            statistics=context.statistics,
            liquidity_metrics=context.liquidity_metrics
        )

        # Persist using Repository
        await self._repository.save_liquidity_universe(qualified_universe)
        logger.info(f"Successfully generated and saved Liquidity Qualified Universe: {liquidity_universe_id}")

        return LiquidityFilterResult(universe=qualified_universe)
