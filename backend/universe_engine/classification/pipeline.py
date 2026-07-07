from typing import List
from backend.universe_engine.contracts.classification import IClassificationStage, IClassificationDataProvider
from backend.universe_engine.classification.models import UniverseClassificationContext
from backend.core.logger import get_logger

logger = get_logger(__name__)

class UniverseClassificationPipeline:
    """
    Executes a sequence of classification stages on the certified universe.
    """
    def __init__(self):
        self._stages: List[IClassificationStage] = []

    def register_stage(self, stage: IClassificationStage) -> None:
        """Adds a classification stage to the pipeline."""
        self._stages.append(stage)
        logger.debug(f"Registered classification stage: {stage.name}")

    async def execute(
        self, 
        context: UniverseClassificationContext, 
        provider: IClassificationDataProvider
    ) -> UniverseClassificationContext:
        """
        Executes all registered stages sequentially.
        """
        logger.info(f"Executing Classification Pipeline with {len(self._stages)} stages.")

        for stage in self._stages:
            logger.debug(f"Executing stage: {stage.name}")
            try:
                await stage.execute(context, provider)
            except Exception as e:
                logger.error(f"Classification stage {stage.name} failed: {str(e)}")
                raise

        logger.info("Classification Pipeline execution completed successfully.")
        return context
