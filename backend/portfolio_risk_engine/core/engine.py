import time
from typing import List, cast
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot
from backend.portfolio_risk_engine.models.report import PortfolioRiskReport, ValidationResult
from backend.portfolio_risk_engine.validation.contracts import IPortfolioRiskValidationLayer
from backend.portfolio_risk_engine.pipeline.pipeline import PortfolioRiskPipeline
from backend.portfolio_risk_engine.models.evidence import (
    PortfolioExposureEvidence, PositionExposureEvidence,
    SectorExposureEvidence, CorrelationEvidence,
    DailyRiskEvidence, OpenRiskEvidence
)
from backend.portfolio_risk_engine.core.builder import PortfolioRiskSnapshotBuilder
from backend.portfolio_risk_engine.contracts.repository import IPortfolioRiskSnapshotRepository
from backend.portfolio_risk_engine.contracts.providers import IPortfolioSnapshotProvider
from backend.portfolio_risk_engine.exceptions.exceptions import PortfolioRiskValidationError

class PortfolioRiskEngine:
    """
    Thin orchestrator for Phase 11.4 Portfolio Risk Validation Engine.
    Executes context validation, pipeline stages, snapshot construction, and persistence.
    """
    
    def __init__(
        self,
        validation_layers: List[IPortfolioRiskValidationLayer],
        pipeline: PortfolioRiskPipeline,
        repository: IPortfolioRiskSnapshotRepository
    ):
        self._validation_layers = validation_layers
        self._pipeline = pipeline
        self._repository = repository
        
    async def execute(self, context: PortfolioRiskContext, provider: IPortfolioSnapshotProvider) -> PortfolioRiskSnapshot:
        start_time = time.perf_counter()
        
        # 1. Validation
        if context.configuration.validation_enabled:
            all_errors = []
            for layer in self._validation_layers:
                result = await layer.validate(context)
                if not result.is_valid:
                    all_errors.extend(result.errors)
                    
            if all_errors:
                if context.configuration.fail_fast:
                    raise PortfolioRiskValidationError(f"Validation failed: {all_errors}")
                validation_status = ValidationResult(is_valid=False, errors=all_errors)
            else:
                validation_status = ValidationResult(is_valid=True)
        else:
            validation_status = ValidationResult(is_valid=True)
            
        # 2. Pipeline Execution
        evidence_bag = await self._pipeline.execute(context, provider)
        
        # Determine global validity (if any stage says invalid, entire report is flagged invalid but execution succeeds)
        pipeline_valid = all(e.is_valid for e in evidence_bag.values())
        if not pipeline_valid and validation_status.is_valid:
            validation_status = ValidationResult(is_valid=False, errors=["One or more pipeline exposure limits were exceeded."])
            
        # 3. Report Assembly
        report = PortfolioRiskReport(
            validation_status=validation_status,
            portfolio_exposure_evidence=cast(PortfolioExposureEvidence, evidence_bag.get("portfolio_exposure")),
            position_exposure_evidence=cast(PositionExposureEvidence, evidence_bag.get("position_exposure")),
            sector_exposure_evidence=cast(SectorExposureEvidence, evidence_bag.get("sector_exposure")),
            correlation_evidence=cast(CorrelationEvidence, evidence_bag.get("correlation_exposure")),
            daily_risk_evidence=cast(DailyRiskEvidence, evidence_bag.get("daily_risk")),
            open_risk_evidence=cast(OpenRiskEvidence, evidence_bag.get("open_risk")),
            configuration_version=context.configuration.pipeline_version,
            algorithm_version="1.0.0"
        )
        
        execution_duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        # 4. Snapshot Generation
        snapshot = PortfolioRiskSnapshotBuilder.build(context, report, execution_duration_ms)
        
        # 5. Persistence
        await self._repository.save(snapshot)
        
        return snapshot
