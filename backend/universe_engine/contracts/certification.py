from typing import Protocol, runtime_checkable
from backend.universe_engine.certification.models import (
    CertificationReport,
    UniverseCertificationContext,
    UniverseCertificationResult
)

@runtime_checkable
class IUniverseCertificationRepository(Protocol):
    """
    Contract for persisting certification reports.
    """
    
    async def save_certification_report(self, report: CertificationReport) -> None:
        """Saves a newly generated certification report."""
        ...
        
    async def load_certification_report(self, certification_id: str) -> CertificationReport:
        """Loads a certification report by ID."""
        ...

@runtime_checkable
class IUniverseCertificationFacade(Protocol):
    """
    Contract for the injected facade that runs the full Universe Engine pipeline 
    (Phases 5.1 - 5.6) deterministically or in integration mode.
    """
    
    async def execute_full_pipeline(
        self, 
        run_id: str, 
        mock_dataset: list = None,
        is_incremental: bool = False
    ) -> dict:
        """
        Executes the full pipeline and returns a dictionary of the outputs from each phase:
        - "universe_snapshot"
        - "liquidity_universe"
        - "certified_universe"
        - "classified_universe"
        - "optimized_universe"
        """
        ...

@runtime_checkable
class ICertificationStage(Protocol):
    """
    Contract for an individual stage in the Certification Pipeline.
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        """
        Executes a certification stage (Functional, Determinism, Integrity, Stress).
        Updates the context with results. Raises CertificationVerificationError if it encounters
        a critical unrecoverable failure that should halt the pipeline, otherwise just
        sets the passed flags in context to False.
        """
        ...
