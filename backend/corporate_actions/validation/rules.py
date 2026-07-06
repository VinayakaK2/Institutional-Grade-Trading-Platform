from typing import List, Tuple, Dict
from datetime import date

from backend.corporate_actions.models.action import CorporateAction, ActionType

class ValidationError(Exception):
    pass

class BaseValidationRule:
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> List[Tuple[CorporateAction, str]]:
        """Returns a list of tuples containing the invalid action and the error reason."""
        raise NotImplementedError

class DuplicateActionRule(BaseValidationRule):
    """Detects identical actions (same symbol, type, effective date)."""
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> List[Tuple[CorporateAction, str]]:
        errors = []
        seen = set()
        
        # Populate seen with existing actions
        for action in existing_actions:
            key = (action.symbol.full_name, action.action_type, action.effective_date)
            seen.add(key)
            
        for action in actions:
            key = (action.symbol.full_name, action.action_type, action.effective_date)
            if key in seen:
                errors.append((action, f"Duplicate action detected: {key}"))
            else:
                seen.add(key)
                
        return errors

class ConflictActionRule(BaseValidationRule):
    """Detects conflicting actions on the same day for the same symbol (e.g. Split and Reverse Split)."""
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> List[Tuple[CorporateAction, str]]:
        errors = []
        action_map: Dict[Tuple[str, date], List[CorporateAction]] = {}
        
        all_actions = existing_actions + actions
        
        for action in all_actions:
            key = (action.symbol.full_name, action.effective_date)
            if key not in action_map:
                action_map[key] = []
            action_map[key].append(action)
            
        for action in actions:
            key = (action.symbol.full_name, action.effective_date)
            day_actions = action_map[key]
            
            # Conflict rules: you can't have >1 split/reverse split/bonus on the same day
            structural_types = {ActionType.STOCK_SPLIT, ActionType.REVERSE_SPLIT, ActionType.BONUS_ISSUE}
            structural_count = sum(1 for a in day_actions if a.action_type in structural_types)
            
            if structural_count > 1:
                errors.append((action, f"Conflicting structural actions on {action.effective_date} for {action.symbol.full_name}"))
                
        return errors

class EffectiveDateRule(BaseValidationRule):
    """Ensures effective date is logical."""
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> List[Tuple[CorporateAction, str]]:
        errors = []
        today = date.today()
        
        for action in actions:
            if action.effective_date > today:
                # We can't apply future actions to historical data until they happen
                errors.append((action, f"Effective date {action.effective_date} is in the future"))
        return errors

class RatioValidityRule(BaseValidationRule):
    """Ensures ratios and amounts are mathematically valid."""
    def validate(self, actions: List[CorporateAction], existing_actions: List[CorporateAction]) -> List[Tuple[CorporateAction, str]]:
        errors = []
        for action in actions:
            if action.action_type in {ActionType.STOCK_SPLIT, ActionType.REVERSE_SPLIT, ActionType.BONUS_ISSUE}:
                if action.ratio is None or action.ratio <= 0:
                    errors.append((action, f"Invalid ratio {action.ratio} for {action.action_type}"))
            elif action.action_type == ActionType.CASH_DIVIDEND:
                if action.amount is None or action.amount <= 0:
                    errors.append((action, f"Invalid amount {action.amount} for {action.action_type}"))
        return errors
