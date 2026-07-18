from backend.trade_validation_engine.trade_decision.di.container import TradeDecisionContainer
from backend.trade_validation_engine.optimization.config.config import OptimizationConfig
from backend.trade_validation_engine.optimization.engine.orchestrator import AsyncExecutionOrchestrator
from backend.trade_validation_engine.optimization.engine.cache_resolver import OptimizationCacheResolver
from backend.trade_validation_engine.optimization.engine.optimization_engine import TradeValidationOptimizationEngine
from backend.trade_validation_engine.optimization.repository.memory import InMemoryOptimizationRepository
from backend.trade_validation_engine.optimization.query_service.memory import InMemoryOptimizationQueryService

class OptimizationContainer:
    """
    Dependency Injection container for the Optimization Engine (Phase 10.5).
    """
    def __init__(
        self,
        decision_container: TradeDecisionContainer = None,
        config: OptimizationConfig = None
    ):
        self.decision_container = decision_container or TradeDecisionContainer()
        self.config = config or OptimizationConfig()
        
        self._repository = InMemoryOptimizationRepository()
        self._query_service = InMemoryOptimizationQueryService(self._repository)
        
        self._orchestrator = AsyncExecutionOrchestrator()
        self._cache_resolver = OptimizationCacheResolver(self._repository)
        
        self._engine = TradeValidationOptimizationEngine(
            decision_engine=self.decision_container.engine(),
            orchestrator=self._orchestrator,
            cache_resolver=self._cache_resolver,
            repository=self._repository,
            config=self.config
        )

    def engine(self) -> TradeValidationOptimizationEngine:
        return self._engine

    def repository(self) -> InMemoryOptimizationRepository:
        return self._repository

    def query_service(self) -> InMemoryOptimizationQueryService:
        return self._query_service
