"""
Watchlist Certification Pipeline
================================

Orchestrates sequential execution of certification stages.
"""
from typing import List

from backend.watchlist_engine.certification.contracts import ICertificationPipeline, ICertificationStage
from backend.watchlist_engine.certification.models import CertificationContext


class CertificationPipeline(ICertificationPipeline):
    """
    Executes all registered stages sequentially.
    Aggregates results into the context.
    """
    
    def __init__(self) -> None:
        self._stages: List[ICertificationStage] = []
        
    def register_stage(self, stage: ICertificationStage) -> None:
        self._stages.append(stage)
        
    async def execute(self, context: CertificationContext) -> None:
        """
        Executes stages sequentially and populates the context.
        """
        for stage in self._stages:
            result = await stage.execute(context)
            context.add_result(result)
