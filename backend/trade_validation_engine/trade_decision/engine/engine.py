import logging
from backend.trade_validation_engine.trade_decision.models.models import (
    DecisionContext,
    TradeDecisionSnapshot
)
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport
from backend.trade_validation_engine.trade_decision.pipeline.pipeline import TradeDecisionPipeline
from backend.trade_validation_engine.trade_decision.engine.resolver import DecisionResolver
from backend.trade_validation_engine.trade_decision.engine.builder import TradeDecisionBuilder
from backend.trade_validation_engine.trade_decision.contracts.repository import ITradeDecisionRepository

logger = logging.getLogger(__name__)

class TradeDecisionEngine:
    """
    Main orchestrator for Phase 10.4.
    Loads context, invokes the pipeline, resolves the final decision,
    builds the snapshot, and persists the result.
    """
    def __init__(
        self, 
        pipeline: TradeDecisionPipeline, 
        repository: ITradeDecisionRepository
    ):
        self._pipeline = pipeline
        self._repository = repository

    async def execute(self, context: DecisionContext, validation_report: ValidationReport) -> TradeDecisionSnapshot:
        logger.info(f"Executing Trade Decision Engine for {context.symbol} on {context.timeframe}")
        
        # 1. Pipeline Execution
        stage_results = await self._pipeline.execute(context, validation_report)
        
        # 2. Decision Resolution
        final_state, rejection_reasons = DecisionResolver.resolve(stage_results)
        
        # 3. Decision Building
        snapshot = TradeDecisionBuilder.build(
            context=context,
            final_state=final_state,
            rejection_reasons=rejection_reasons,
            stage_results=stage_results
        )
        
        # 4. Persistence
        await self._repository.save(snapshot)
        
        logger.info(f"Completed Trade Decision Engine. Final State: {snapshot.decision_state.value}")
        return snapshot
