import time
import logging
from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, ValidationReport
from backend.trade_validation_engine.validation_rules.pipeline.pipeline import ValidationPipeline
from backend.trade_validation_engine.validation_rules.engine.builder import ValidationReportBuilder
from backend.trade_validation_engine.validation_rules.contracts.repository import IValidationReportRepository

logger = logging.getLogger(__name__)

class ValidationRulesEngine:
    """
    Stateless orchestrator for the Validation Rules Phase (Phase 10.3).
    Execution Flow:
    AggregatedTradeEvidence -> Rule Pipeline -> ValidationReportBuilder -> ValidationReport -> Repository
    """
    def __init__(
        self,
        pipeline: ValidationPipeline,
        repository: IValidationReportRepository
    ):
        self._pipeline = pipeline
        self._repository = repository

    async def run(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> ValidationReport:
        logger.info(f"Starting Validation Engine for Symbol: {context.symbol}, Timeframe: {context.timeframe}")
        
        start_time = time.perf_counter()
        
        # Ensure context metadata holds the aggregated_trade_snapshot_version for repository querying
        if "aggregated_trade_snapshot_version" not in context.metadata:
            context.metadata["aggregated_trade_snapshot_version"] = context.aggregated_trade_snapshot_version
            
        # Execute the pipeline
        rule_results = await self._pipeline.execute(context, aggregated_evidence)
        
        total_duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Build the final report
        report = ValidationReportBuilder.build(
            context=context,
            rule_results=rule_results,
            total_duration_ms=total_duration_ms
        )
        
        # Persist the report immutably
        await self._repository.save(report)
        
        logger.info(f"Completed Validation Engine. Status: {report.status.value}. Duration: {total_duration_ms}ms")
        
        return report
