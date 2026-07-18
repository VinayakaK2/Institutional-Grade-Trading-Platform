import abc
import time
import logging
from typing import List, Set
from backend.trade_validation_engine.trade_decision.models.models import (
    DecisionContext, 
    StageExecutionResult, 
    DecisionState
)
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport

from backend.trade_validation_engine.trade_decision.exceptions.exceptions import DecisionPipelineError

logger = logging.getLogger(__name__)

class IDecisionStage(abc.ABC):
    """
    Base contract for a stage in the decision pipeline.
    """
    @property
    @abc.abstractmethod
    def stage_id(self) -> str:
        pass
        
    @abc.abstractmethod
    async def execute(self, context: DecisionContext, validation_report: ValidationReport) -> StageExecutionResult:
        pass


class TradeDecisionPipeline:
    """
    Orchestrates the ordered execution of decision stages.
    Supports context propagation and fail-fast behavior.
    """
    def __init__(self) -> None:
        self._stages: List[IDecisionStage] = []
        self._stage_ids: Set[str] = set()

    def register_stage(self, stage: IDecisionStage) -> None:
        if stage.stage_id in self._stage_ids:
            raise DecisionPipelineError(f"Duplicate stage registration rejected for: {stage.stage_id}")
        self._stages.append(stage)
        self._stage_ids.add(stage.stage_id)
        
    def get_stages(self) -> List[IDecisionStage]:
        return self._stages

    async def execute(self, context: DecisionContext, validation_report: ValidationReport) -> List[StageExecutionResult]:
        results: List[StageExecutionResult] = []
        
        for stage in self._stages:
            logger.debug(f"Executing decision stage: {stage.stage_id}")
            
            try:
                result = await stage.execute(context, validation_report)
                results.append(result)
                
                if context.configuration.fail_fast and result.state != DecisionState.VALID:
                    logger.info(f"Pipeline fail-fast triggered at stage {stage.stage_id}")
                    break
                    
            except Exception as e:
                logger.error(f"Error executing stage {stage.stage_id}: {str(e)}")
                raise
                
        return results
