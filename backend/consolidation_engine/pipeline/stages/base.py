from abc import ABC, abstractmethod
from backend.consolidation_engine.models.models import ConsolidationExecutionContext, ConsolidationSnapshot

class IConsolidationStage(ABC):
    """
    Base contract for a Consolidation Pipeline stage.
    """
    
    @abstractmethod
    def execute(self, context: ConsolidationExecutionContext, snapshot: ConsolidationSnapshot) -> ConsolidationSnapshot:
        """
        Executes the stage logic using the provided immutable context and current snapshot state.
        Returns a newly updated snapshot (or same if unmodified).
        """
        pass
