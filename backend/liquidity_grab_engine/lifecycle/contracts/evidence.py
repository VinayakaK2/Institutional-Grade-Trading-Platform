from abc import ABC, abstractmethod
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import (
    ContinuationEvidence,
    WeakeningEvidence,
    FailureEvidence,
    ExpirationEvidence
)

class IEvidenceStrategy(ABC):
    @property
    @abstractmethod
    def priority(self) -> int:
        pass
        
    @property
    @abstractmethod
    def strategy_id(self) -> str:
        pass

class IContinuationStrategy(IEvidenceStrategy):
    @abstractmethod
    def evaluate(self, context: LiquidityGrabLifecycleContext) -> ContinuationEvidence:
        pass

class IWeakeningStrategy(IEvidenceStrategy):
    @abstractmethod
    def evaluate(self, context: LiquidityGrabLifecycleContext) -> WeakeningEvidence:
        pass

class IFailureStrategy(IEvidenceStrategy):
    @abstractmethod
    def evaluate(self, context: LiquidityGrabLifecycleContext) -> FailureEvidence:
        pass

class IExpirationStrategy(IEvidenceStrategy):
    @abstractmethod
    def evaluate(self, context: LiquidityGrabLifecycleContext) -> ExpirationEvidence:
        pass
