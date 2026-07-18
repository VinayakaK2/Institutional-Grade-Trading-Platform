from backend.trade_validation_engine.trade_decision.pipeline.pipeline import TradeDecisionPipeline
from backend.trade_validation_engine.trade_decision.engine.engine import TradeDecisionEngine
from backend.trade_validation_engine.trade_decision.repository.memory import InMemoryTradeDecisionRepository
from backend.trade_validation_engine.trade_decision.query_service.memory import InMemoryTradeDecisionQueryService

class TradeDecisionContainer:
    """
    Deterministic manual DI container for Phase 10.4.
    """
    def __init__(self) -> None:
        self.repository = InMemoryTradeDecisionRepository()
        self.query_service = InMemoryTradeDecisionQueryService(self.repository)
        self.pipeline = TradeDecisionPipeline()
        self.engine_instance = TradeDecisionEngine(
            pipeline=self.pipeline,
            repository=self.repository
        )
        
    def engine(self) -> TradeDecisionEngine:
        return self.engine_instance
