from abc import ABC, abstractmethod
from backend.universe_engine.models.universe import UniverseExecutionContext, StageResult

class IUniverseStage(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def execute(self, context: UniverseExecutionContext) -> StageResult:
        pass

class IUniversePipeline(ABC):
    @abstractmethod
    def register_stage(self, stage: IUniverseStage) -> None:
        pass

    @abstractmethod
    async def execute(self, context: UniverseExecutionContext) -> UniverseExecutionContext:
        pass
