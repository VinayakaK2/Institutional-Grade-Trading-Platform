import logging
import time
from typing import List
from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, RuleValidationResult
from backend.trade_validation_engine.validation_rules.registry.registry import RuleRegistry
from backend.trade_validation_engine.validation_rules.exceptions.exceptions import RuleExecutionError

logger = logging.getLogger(__name__)

class ValidationPipeline:
    """
    Executes the sequence of rules retrieved from the RuleRegistry against the aggregated evidence.
    Supports fail_fast logic.
    """
    def __init__(self, registry: RuleRegistry):
        self._registry = registry

    async def execute(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> List[RuleValidationResult]:
        enabled_rules = context.configuration.enabled_rules if hasattr(context.configuration, "enabled_rules") else None
        rules = self._registry.get_ordered_rules(enabled_rules=enabled_rules)
        
        results: List[RuleValidationResult] = []
        
        logger.info("Pipeline Summary: Starting Validation Rules Pipeline")
        
        for rule in rules:
            logger.debug(f"Rule Start: {rule.rule_id}")
            start_time = time.perf_counter()
            
            try:
                result = await rule.validate(context, aggregated_evidence)
            except Exception as e:
                logger.error(f"Rule {rule.rule_id} crashed: {str(e)}")
                raise RuleExecutionError(f"Rule {rule.rule_id} failed unexpectedly: {str(e)}") from e
                
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Diagnostic updates
            if context.configuration.diagnostic_mode:
                updated_metadata = dict(result.metadata)
                updated_metadata["execution_duration_ms"] = duration_ms
                # Pydantic v2 requires model_copy(update=...)
                result = result.model_copy(update={"metadata": updated_metadata})
                
            results.append(result)
            
            logger.debug(f"Rule End: {rule.rule_id}")
            logger.debug(f"Execution Duration: {duration_ms}ms")
            logger.info(f"Validation Status: {rule.rule_id} -> {result.status}")
            
            if result.status == "FAIL" and context.configuration.fail_fast:
                logger.warning(f"Pipeline Summary: Fail fast triggered by {rule.rule_id}")
                break
                
        logger.info("Pipeline Summary: Completed Validation Rules Pipeline")
        return results
