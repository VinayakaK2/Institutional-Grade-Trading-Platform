from abc import ABC, abstractmethod
from typing import List
from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.models.models import ValidationStageResult, ValidationPipelineResult

class IValidationStage(ABC):
    """
    Contract for a generic validation stage.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the stage."""
        pass
        
    @abstractmethod
    def execute(self, context: TradeValidationExecutionContext) -> ValidationStageResult:
        """
        Executes the validation logic for this stage.
        """
        pass

class TradeValidationPipeline:
    """
    Reusable pipeline framework for Trade Validation.
    Executes registered stages sequentially.
    """
    
    def __init__(self, stages: List[IValidationStage]):
        self._stages = stages
        
    def execute(self, context: TradeValidationExecutionContext) -> ValidationPipelineResult:
        """
        Executes all stages in order.
        Respects the fail_fast configuration in the context.
        """
        results: List[ValidationStageResult] = []
        pipeline_success = True
        
        for stage in self._stages:
            try:
                result = stage.execute(context)
                results.append(result)
                
                if not result.success:
                    pipeline_success = False
                    if context.configuration.fail_fast:
                        break
                        
            except Exception as e:
                # Catch unexpected exceptions and wrap them
                error_result = ValidationStageResult(
                    stage_name=stage.name,
                    success=False,
                    error_message=f"Unhandled exception during execution: {str(e)}"
                )
                results.append(error_result)
                pipeline_success = False
                
                if context.configuration.fail_fast:
                    break

        return ValidationPipelineResult(
            success=pipeline_success,
            stage_results=results
        )
