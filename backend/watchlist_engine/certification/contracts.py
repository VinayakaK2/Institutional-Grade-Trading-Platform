"""
Watchlist Certification Contracts
=================================

Abstract interfaces for the Certification Framework.
"""
from abc import ABC, abstractmethod

from backend.watchlist_engine.certification.models import CertificationStageResult, CertificationContext


class ICertificationStage(ABC):
    """
    Contract for an individual stage in the Certification Pipeline.
    Returns an immutable CertificationStageResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this certification stage."""
        ...

    @abstractmethod
    async def execute(self, context: CertificationContext) -> CertificationStageResult:
        """
        Executes this certification stage against the provided context.

        Returns:
            An immutable CertificationStageResult describing the outcome.
        """
        ...


class ICertificationPipeline(ABC):
    """
    Contract for the Certification Execution Pipeline.
    Manages ordered registration and sequential execution of stages.
    """

    @abstractmethod
    def register_stage(self, stage: ICertificationStage) -> None:
        """Registers a certification stage for ordered execution."""
        ...

    @abstractmethod
    async def execute(self, context: CertificationContext) -> None:
        """
        Executes all registered stages sequentially.
        Aggregates results into the provided CertificationContext.
        """
        ...
