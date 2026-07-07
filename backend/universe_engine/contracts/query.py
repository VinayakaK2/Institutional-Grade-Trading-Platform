"""
Query Service Contracts for Universe Read Models.
Provides a read-side abstraction over the underlying repositories.
"""
from abc import ABC, abstractmethod
from typing import Optional

from backend.universe_engine.models.read_views import CandidateUniverseView


class ICandidateUniverseQueryService(ABC):
    """
    Dedicated read-side service for projecting the Classified Universe into
    a CandidateUniverseView suitable for the Candidate Selection Engine.
    
    This abstracts away the underlying repository details and classification
    complexities, adhering to the read-model pattern requested by architecture.
    """

    @abstractmethod
    async def load_latest(self) -> Optional[CandidateUniverseView]:
        """
        Loads the most recent Classified Universe projected as a CandidateUniverseView.
        """
        pass

    @abstractmethod
    async def load_by_version(self, version: int) -> Optional[CandidateUniverseView]:
        """
        Loads a specific version of the Classified Universe projected as a CandidateUniverseView.
        """
        pass
