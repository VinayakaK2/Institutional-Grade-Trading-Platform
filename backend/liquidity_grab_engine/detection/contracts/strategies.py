from abc import ABC, abstractmethod
from typing import Optional
from backend.liquidity_grab_engine.detection.models.context import LiquidityGrabDetectionContext

class ISupportBreakDetectionStrategy(ABC):
    """
    Interface for detecting support breaks.
    """
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the specific version of this algorithm."""
        pass

    @abstractmethod
    def detect(self, context: LiquidityGrabDetectionContext) -> bool:
        pass

class IRecoveryDetectionStrategy(ABC):
    """
    Interface for detecting recoveries back above support.
    """
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the specific version of this algorithm."""
        pass

    @abstractmethod
    def detect(self, context: LiquidityGrabDetectionContext) -> bool:
        pass

class IFalseBreakValidationStrategy(ABC):
    """
    Interface for validating if the break was a false break.
    """
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the specific version of this algorithm."""
        pass

    @abstractmethod
    def validate(self, context: LiquidityGrabDetectionContext) -> bool:
        pass
