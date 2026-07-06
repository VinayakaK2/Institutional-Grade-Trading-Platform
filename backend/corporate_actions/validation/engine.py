from typing import List, Tuple

from backend.corporate_actions.models.action import CorporateAction, ActionStatus
from backend.corporate_actions.validation.rules import (
    BaseValidationRule, DuplicateActionRule, ConflictActionRule, EffectiveDateRule, RatioValidityRule
)

class ValidationEngine:
    """Runs a series of validation rules against a batch of corporate actions."""
    
    def __init__(self, rules: List[BaseValidationRule] = None):
        self.rules = rules or [
            DuplicateActionRule(),
            ConflictActionRule(),
            EffectiveDateRule(),
            RatioValidityRule()
        ]
        
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> Tuple[List[CorporateAction], List[Tuple[CorporateAction, str]]]:
        """
        Validates actions against rules and existing actions.
        Returns (valid_actions, list of (invalid_action, error_reason)).
        """
        valid_actions = []
        errors = []
        
        # We need to process sequentially because a single action might fail multiple rules
        # But we only want to record it once.
        failed_action_ids = set()
        
        for rule in self.rules:
            rule_errors = rule.validate(actions, existing_actions)
            for invalid_action, reason in rule_errors:
                if invalid_action.id not in failed_action_ids:
                    errors.append((invalid_action, reason))
                    failed_action_ids.add(invalid_action.id)
                    
        for action in actions:
            if action.id not in failed_action_ids:
                action.status = ActionStatus.VALIDATED
                valid_actions.append(action)
            else:
                # We could set status to REJECTED, but the return tuple makes it clear.
                pass
                
        return valid_actions, errors
