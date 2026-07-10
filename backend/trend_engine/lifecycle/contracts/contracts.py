from abc import ABC, abstractmethod
from typing import Optional
from backend.trend_engine.lifecycle.models.models import TrendLifecycleSnapshot
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.quality.models.models import TrendQualitySnapshot

class ITrendLifecycleStage(ABC):
    """
    Interface for a Trend Lifecycle Pipeline stage.
    """
    @abstractmethod
    async def execute(self, context: LifecycleExecutionContext) -> None:
        """Execute the lifecycle stage, updating the context directly."""
        pass

class ITrendLifecycleEngine(ABC):
    """
    Interface for the Trend Lifecycle Engine.
    """
    @abstractmethod
    async def evaluate_lifecycle(
        self, 
        trend_snapshot: TrendSnapshot, 
        quality_snapshot: TrendQualitySnapshot
    ) -> TrendLifecycleSnapshot:
        """
        Evaluate the lifecycle of trends given their detection and quality snapshots.
        """
        pass

class ITrendLifecycleRepository(ABC):
    """
    Interface for persistence of Trend Lifecycle Snapshots.
    """
    @abstractmethod
    async def save_lifecycle_snapshot(self, snapshot: TrendLifecycleSnapshot) -> None:
        pass
        
    @abstractmethod
    async def get_lifecycle_snapshot(self, snapshot_id: str) -> Optional[TrendLifecycleSnapshot]:
        pass
        
    @abstractmethod
    async def get_latest_for_parent_snapshot(self, parent_trend_snapshot_id: str) -> Optional[TrendLifecycleSnapshot]:
        pass

    @abstractmethod
    async def exists_for_parent_snapshot(self, parent_trend_snapshot_id: str) -> bool:
        pass
