from backend.trade_validation_engine.contracts.repository import ITradeValidationRepository
from backend.trade_validation_engine.contracts.query_service import ITradeValidationQueryService
from backend.trade_validation_engine.repository.memory import InMemoryTradeValidationRepository
from backend.trade_validation_engine.query_service.memory import InMemoryTradeValidationQueryService
from backend.trade_validation_engine.pipeline.pipeline import TradeValidationPipeline
from backend.trade_validation_engine.engine.engine import TradeValidationEngine

class TradeValidationContainer:
    """
    Dependency Injection Container for the Trade Validation Engine.
    """
    def __init__(self):
        self._repository: ITradeValidationRepository = InMemoryTradeValidationRepository()
        
        # In memory query service shares storage with the in memory repository
        if isinstance(self._repository, InMemoryTradeValidationRepository):
            self._query_service: ITradeValidationQueryService = InMemoryTradeValidationQueryService(self._repository._storage)
        else:
            raise ValueError("Unsupported repository type for DI container initialization")
            
        self._pipeline = TradeValidationPipeline(stages=[])
        
        self._engine = TradeValidationEngine(
            pipeline=self._pipeline,
            repository=self._repository
        )
        
    @property
    def engine(self) -> TradeValidationEngine:
        return self._engine
        
    @property
    def repository(self) -> ITradeValidationRepository:
        return self._repository
        
    @property
    def query_service(self) -> ITradeValidationQueryService:
        return self._query_service
