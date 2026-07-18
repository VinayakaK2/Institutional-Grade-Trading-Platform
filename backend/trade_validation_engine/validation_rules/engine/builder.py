import hashlib
from typing import List
from backend.trade_validation_engine.validation_rules.models.models import (
    ValidationContext,
    RuleValidationResult,
    ValidationReportSummary,
    ValidationReport,
    ValidationStatus
)

class ValidationReportBuilder:
    """
    Constructs the immutable ValidationReport from the executed pipeline results.
    Separates the construction of the report from the orchestration engine.
    """
    
    @staticmethod
    def build(
        context: ValidationContext, 
        rule_results: List[RuleValidationResult],
        total_duration_ms: int
    ) -> ValidationReport:
        
        passed_count = sum(1 for r in rule_results if r.status == "PASS")
        failed_count = sum(1 for r in rule_results if r.status == "FAIL")
        skipped_count = sum(1 for r in rule_results if r.status == "SKIP")
        total_rules = len(rule_results)
        
        status = ValidationStatus.PASS if (failed_count == 0 and total_rules > 0) else ValidationStatus.FAIL
        
        summary = ValidationReportSummary(
            total_rules_executed=total_rules,
            passed_rules=passed_count,
            failed_rules=failed_count,
            skipped_rules=skipped_count,
            total_duration_ms=total_duration_ms
        )
        
        # Generate hash of configuration if not already a string (using repr for deterministic hashing)
        # Assuming ValidationRulesConfig is frozen pydantic model, model_dump_json is deterministic if ordered
        config_hash = hashlib.sha256(context.configuration.model_dump_json().encode('utf-8')).hexdigest()
        
        # Validation ID based on context inputs
        payload = f"{context.symbol}_{context.timeframe}_{context.dataset_version}_{context.aggregated_trade_snapshot_version}_{config_hash}"
        validation_id = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        return ValidationReport(
            validation_id=validation_id,
            symbol=context.symbol,
            timeframe=context.timeframe,
            dataset_version=context.dataset_version,
            configuration_hash=config_hash,
            validation_pipeline_version=context.configuration.pipeline_version,
            status=status,
            rule_results=rule_results,
            summary=summary,
            metadata=context.metadata
        )
