import time
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_quality_engine.validation.structural import StructuralValidator
from backend.paper_execution_quality_engine.validation.consistency import ConsistencyValidator
from backend.paper_execution_quality_engine.core.stages.market_impact import MarketImpactStage
from backend.paper_execution_quality_engine.core.stages.slippage import SlippageStage
from backend.paper_execution_quality_engine.core.stages.spread import SpreadStage
from backend.paper_execution_quality_engine.core.stages.gap import GapStage
from backend.paper_execution_quality_engine.core.stages.liquidity import LiquidityStage
from backend.paper_execution_quality_engine.builders.snapshot_builder import PaperExecutionQualitySnapshotBuilder
from backend.paper_execution_quality_engine.contracts.repository import IPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.logging.logger import PaperExecutionQualityLogger
from backend.paper_execution_quality_engine.exceptions.exceptions import (
    PaperExecutionQualityValidationError, 
    PaperExecutionQualityConsistencyError, 
    PaperExecutionQualityCalculationError,
    PaperExecutionQualityPersistenceError
)
from backend.paper_execution_quality_engine.models.execution_quality import ExecutionQualityReport

class PaperExecutionQualityEngine:
    """
    Central deterministic orchestrator for the Paper Execution Quality Pipeline.
    """
    def __init__(self, repository: IPaperExecutionQualityRepository, consistency_validator: ConsistencyValidator):
        self._structural_validator = StructuralValidator()
        self._consistency_validator = consistency_validator
        
        self._stages = [
            MarketImpactStage(),
            SlippageStage(),
            SpreadStage(),
            GapStage(),
            LiquidityStage()
        ]
        
        self._snapshot_builder = PaperExecutionQualitySnapshotBuilder()
        self._repository = repository
        self._logger = PaperExecutionQualityLogger()

    async def execute(self, execution_context: PaperExecutionQualityExecutionContext) -> PaperExecutionQualitySnapshot:
        start_time = time.perf_counter()
        pipeline_context = PaperExecutionQualityPipelineContext(execution_context=execution_context)
        
        try:
            self._logger.log_execution_start(execution_context)
            
            # Structural Validation
            struct_report = self._structural_validator.validate(execution_context)
            for warning in struct_report.warnings:
                pipeline_context.diagnostics.warnings.append(warning)
                self._logger.log_validation_warning(warning)
            if not struct_report.passed:
                pipeline_context.diagnostics.validation_errors.extend(struct_report.errors)
                raise PaperExecutionQualityValidationError(" | ".join(struct_report.errors))

            # Consistency Validation
            consist_report = await self._consistency_validator.validate(execution_context)
            for warning in consist_report.warnings:
                pipeline_context.diagnostics.warnings.append(warning)
                self._logger.log_validation_warning(warning)
            if not consist_report.passed:
                pipeline_context.diagnostics.validation_errors.extend(consist_report.errors)
                raise PaperExecutionQualityConsistencyError(" | ".join(consist_report.errors))

            # Run Stages
            for stage in self._stages:
                stage_start = time.perf_counter()
                await stage.execute(execution_context, pipeline_context)
                pipeline_context.telemetry.stage_timings[stage.__class__.__name__] = (time.perf_counter() - stage_start) * 1000.0

            # 4. Compile Report
            pipeline_context.execution_quality_report = pipeline_context.require_complete()

            # 5. Build Snapshot
            snapshot = self._snapshot_builder.build(execution_context, pipeline_context)
            
            # 6. Persist
            self._repository.save(snapshot)
            return snapshot

        except Exception as e:
            self._logger.log_error(e)
            raise
