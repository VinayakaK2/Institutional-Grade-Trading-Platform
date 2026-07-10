"""
Trend Quality Contracts
=======================

Abstract base classes for the Trend Quality Engine dependencies.
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.quality.models.models import TrendQualitySnapshot
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext


class ITrendQualityStage(ABC):
    """
    Contract for a single evaluation stage within the Trend Quality Pipeline.
    Stages must remain completely stateless and execute purely deterministically.
    """
    
    @abstractmethod
    async def execute(self, context: QualityExecutionContext) -> None:
        """
        Executes the stage logic and updates the appropriate result property 
        on the QualityExecutionContext. Must not raise unhandled exceptions.
        """
        pass


class ITrendQualityRepository(ABC):
    """
    Contract for the Trend Quality persistent storage.
    Must be insert-only, idempotent, and async.
    """
    
    @abstractmethod
    async def save_quality_snapshot(self, snapshot: TrendQualitySnapshot) -> None:
        """Persists a new TrendQualitySnapshot."""
        pass
        
    @abstractmethod
    async def get_quality_snapshot(self, snapshot_id: str) -> Optional[TrendQualitySnapshot]:
        """Retrieves a TrendQualitySnapshot by ID."""
        pass

    @abstractmethod
    async def get_latest_quality_for_trend(self, trend_snapshot_id: str) -> Optional[TrendQualitySnapshot]:
        """Retrieves the latest TrendQualitySnapshot for a given parent TrendSnapshot."""
        pass


class ITrendQualityEngine(ABC):
    """
    Contract for the Trend Quality Engine orchestration.
    """
    
    @abstractmethod
    async def evaluate_trend_quality(self, parent_snapshot: TrendSnapshot) -> TrendQualitySnapshot:
        """
        Evaluates the structural quality of a detected trend.
        Raises exceptions on invalid configurations or unrecoverable repository errors.
        """
        pass
