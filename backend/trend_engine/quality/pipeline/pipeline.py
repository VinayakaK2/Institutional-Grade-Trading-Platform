"""
Trend Quality Pipeline
======================

Orchestrates the ordered execution of independent evaluation stages 
and normalization.
"""

from typing import List
from backend.trend_engine.quality.contracts.contracts import ITrendQualityStage
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext

class TrendQualityPipeline:
    """
    Executes stages in a strictly defined order.
    Validation -> [Strength, Consistency, Pullback, Persistence] -> Normalization
    """
    
    def __init__(self, stages: List[ITrendQualityStage]):
        self._stages = stages
        
    async def execute(self, context: QualityExecutionContext) -> None:
        """
        Runs all configured stages. 
        Failures inside a stage must be caught and logged as warnings, 
        but should not crash the pipeline unless unrecoverable.
        """
        for stage in self._stages:
            try:
                await stage.execute(context)
            except Exception as e:
                # Top-level safety net for unhandled exceptions
                context.warnings.append(f"Stage {stage.__class__.__name__} failed: {e}")
