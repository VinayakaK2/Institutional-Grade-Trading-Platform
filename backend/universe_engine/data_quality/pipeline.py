import time
from typing import List

from backend.universe_engine.contracts.data_quality import (
    IDataQualityStage,
    IDataQualityDataProvider,
    IMarketCalendarProvider,
    ICorporateActionProvider,
)
from backend.universe_engine.data_quality.models import DataQualityFilterContext
from backend.universe_engine.data_quality.exceptions import DataQualityPipelineError
from backend.core.logger import get_logger

logger = get_logger(__name__)


class DataQualityFilterPipeline:
    """
    Executes a sequence of Data Quality stages implementing a Fail Fast policy.
    Once an instrument fails a stage, it is removed from context.certified_instruments
    and will not be processed by subsequent stages.
    """

    def __init__(self):
        self._stages: List[IDataQualityStage] = []

    def register_stage(self, stage: IDataQualityStage) -> None:
        self._stages.append(stage)
        logger.debug(f"Registered data quality pipeline stage: {stage.name}")

    async def execute(
        self,
        context: DataQualityFilterContext,
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider,
    ) -> DataQualityFilterContext:
        logger.info(
            f"Starting data quality pipeline execution for run_id: {context.run_id}"
        )

        start_time = time.perf_counter()

        for stage in self._stages:
            logger.info(f"Executing data quality stage: {stage.name}")
            try:
                await stage.execute(
                    context, data_provider, calendar_provider, corporate_action_provider
                )
            except Exception as e:
                logger.error(
                    f"Error executing stage {stage.name}: {str(e)}", exc_info=True
                )
                raise DataQualityPipelineError(
                    f"Stage {stage.name} failed: {str(e)}"
                ) from e

            logger.info(
                f"Stage {stage.name} finished. Surviving instruments: {len(context.certified_instruments)}"
            )

            if not context.certified_instruments:
                logger.info(
                    "No instruments survived. Halting pipeline execution early."
                )
                break

        duration = (time.perf_counter() - start_time) * 1000
        context.statistics.processing_time_ms = duration

        logger.info(f"Finished data quality pipeline execution in {duration:.2f}ms.")
        return context
