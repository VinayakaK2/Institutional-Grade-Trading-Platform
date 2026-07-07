from typing import List
import time
from backend.universe_engine.contracts.liquidity import (
    ILiquidityStage,
    ILiquidityDataProvider,
    IFundamentalDataProvider
)
from backend.universe_engine.liquidity.models import LiquidityFilterContext
from backend.core.logger import get_logger

logger = get_logger(__name__)

class LiquidityFilterPipeline:
    def __init__(self):
        self._stages: List[ILiquidityStage] = []

    def register_stage(self, stage: ILiquidityStage) -> None:
        self._stages.append(stage)
        logger.debug(f"Registered liquidity pipeline stage: {stage.name}")

    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider,
        fundamental_provider: IFundamentalDataProvider
    ) -> LiquidityFilterContext:
        logger.info(f"Starting liquidity pipeline execution for run_id: {context.run_id}")
        
        start_time = time.perf_counter()
        
        for stage in self._stages:
            logger.info(f"Executing liquidity stage: {stage.name}")
            await stage.execute(context, data_provider, fundamental_provider)
            logger.info(f"Stage {stage.name} finished. Qualified instruments: {len(context.qualified_instruments)}")
            
        duration = (time.perf_counter() - start_time) * 1000
        context.statistics.processing_time_ms = duration
        
        logger.info(f"Finished liquidity pipeline execution in {duration:.2f}ms.")
        return context
