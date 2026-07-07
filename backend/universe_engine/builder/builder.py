from backend.universe_engine.contracts.engine import IUniverseEngine
from backend.universe_engine.contracts.pipeline import IUniversePipeline
from backend.universe_engine.models.universe import UniverseResult
from backend.universe_engine.builder.config import MarketBuilderConfig
from backend.universe_engine.stages.filters import (
    ExchangeFilterStage,
    MarketSegmentFilterStage,
    InstrumentTypeFilterStage,
    TradingStatusFilterStage,
    DelistedFilterStage,
)
from backend.core.logger import get_logger

logger = get_logger(__name__)

class MarketUniverseBuilder:
    """
    Orchestration layer for constructing the tradable market universe.
    
    This builder takes a configured UniverseEngine and a MarketBuilderConfig,
    instantiates the required filter stages, and registers them with the
    engine's pipeline.
    """
    
    def __init__(self, engine: IUniverseEngine, pipeline: IUniversePipeline, config: MarketBuilderConfig):
        self._engine = engine
        self._pipeline = pipeline
        self._config = config
        
        self._register_stages()

    def _register_stages(self) -> None:
        """
        Instantiates and registers the filter stages based on configuration.
        The order of registration is the order of execution.
        """
        logger.info("Registering Market Universe Builder stages.")
        
        # 1. Exchange Selection
        if self._config.allowed_exchanges:
            self._pipeline.register_stage(ExchangeFilterStage(self._config.allowed_exchanges))
            
        # 2. Market Selection
        if self._config.allowed_market_segments:
            self._pipeline.register_stage(MarketSegmentFilterStage(self._config.allowed_market_segments))
            
        # 3. Instrument Type Filter
        if self._config.allowed_instrument_types:
            self._pipeline.register_stage(InstrumentTypeFilterStage(self._config.allowed_instrument_types))
            
        # 4. Trading Status Filter
        if self._config.rejected_trading_statuses:
            self._pipeline.register_stage(TradingStatusFilterStage(self._config.rejected_trading_statuses))
            
        # 5. Delisted Instrument Filter
        if self._config.remove_delisted:
            self._pipeline.register_stage(DelistedFilterStage(self._config.remove_delisted))

    async def build(self, run_id: str) -> UniverseResult:
        """
        Executes the universe generation process.
        
        Args:
            run_id: Unique identifier for this build run.
            
        Returns:
            UniverseResult containing the immutable UniverseSnapshot.
        """
        logger.info(f"MarketUniverseBuilder starting build for run_id: {run_id}")
        return await self._engine.generate_universe(run_id)
