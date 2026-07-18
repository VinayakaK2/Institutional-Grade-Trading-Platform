from backend.trade_validation_engine.validation_rules.config.config import ValidationRulesConfig
from backend.trade_validation_engine.validation_rules.registry.registry import RuleRegistry
from backend.trade_validation_engine.validation_rules.pipeline.pipeline import ValidationPipeline
from backend.trade_validation_engine.validation_rules.engine.engine import ValidationRulesEngine
from backend.trade_validation_engine.validation_rules.repository.memory import InMemoryValidationReportRepository
from backend.trade_validation_engine.validation_rules.query_service.memory import InMemoryValidationQueryService

from backend.trade_validation_engine.validation_rules.rules.evidence_validation import (
    TrendEvidenceRule,
    ConsolidationEvidenceRule,
    LiquidityGrabEvidenceRule
)
from backend.trade_validation_engine.validation_rules.rules.consistency_validation import (
    DatasetConsistencyRule,
    SnapshotLineageRule
)

class ValidationRulesContainer:
    """
    DI Container for Phase 10.3 (Validation Rules Engine).
    """
    def __init__(self, config: ValidationRulesConfig = None):
        self._config = config or ValidationRulesConfig()
        self._repository = InMemoryValidationReportRepository()
        self._query_service = InMemoryValidationQueryService(self._repository)
        
        self._registry = RuleRegistry()
        self._pipeline = ValidationPipeline(self._registry)
        
        self._engine = ValidationRulesEngine(
            pipeline=self._pipeline,
            repository=self._repository
        )
        
    def config(self) -> ValidationRulesConfig:
        return self._config
        
    def repository(self) -> InMemoryValidationReportRepository:
        return self._repository
        
    def query_service(self) -> InMemoryValidationQueryService:
        return self._query_service
        
    def registry(self) -> RuleRegistry:
        return self._registry
        
    def pipeline(self) -> ValidationPipeline:
        return self._pipeline
        
    def engine(self) -> ValidationRulesEngine:
        return self._engine
        
    def register_default_rules(self):
        """Registers the standard validation rules"""
        self._registry.register(TrendEvidenceRule())
        self._registry.register(ConsolidationEvidenceRule())
        self._registry.register(LiquidityGrabEvidenceRule())
        self._registry.register(DatasetConsistencyRule())
        self._registry.register(SnapshotLineageRule())
