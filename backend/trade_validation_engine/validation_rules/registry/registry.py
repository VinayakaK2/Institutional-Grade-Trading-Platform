import logging
from typing import List, Dict, Optional
from backend.trade_validation_engine.validation_rules.rules.base import IValidationRule

logger = logging.getLogger(__name__)

class RuleRegistry:
    """
    Registry for Validation Rules.
    Supports deterministic ordered execution based on rule priority.
    """
    def __init__(self):
        self._rules: Dict[str, IValidationRule] = {}

    def register(self, rule: IValidationRule) -> None:
        if rule.rule_id in self._rules:
            logger.warning(f"Overwriting existing rule in registry: {rule.rule_id}")
        self._rules[rule.rule_id] = rule
        logger.debug(f"Registered rule: {rule.rule_id} (Priority: {rule.priority})")

    def get_ordered_rules(self, enabled_rules: Optional[List[str]] = None) -> List[IValidationRule]:
        """
        Retrieves rules in deterministic order (sorted by priority).
        Optionally filters by the enabled_rules list from config.
        """
        active_rules = list(self._rules.values())
        if enabled_rules is not None:
            active_rules = [r for r in active_rules if r.rule_id in enabled_rules]
            
        return sorted(active_rules, key=lambda r: r.priority)
