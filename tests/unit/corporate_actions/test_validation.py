import pytest
from datetime import datetime, timedelta, date
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.corporate_actions.models.action import CorporateAction, ActionType
from backend.corporate_actions.validation.rules import (
    DuplicateActionRule, ConflictActionRule, EffectiveDateRule, RatioValidityRule
)
from backend.corporate_actions.validation.engine import ValidationEngine

@pytest.fixture
def sym():
    return SymbolReference(symbol="TEST", exchange=ExchangeReference(code="NYSE"))

@pytest.fixture
def base_action(sym):
    return CorporateAction(
        symbol=sym,
        action_type=ActionType.STOCK_SPLIT,
        effective_date=date(2024, 1, 2),
        ratio=2.0
    )

def test_duplicate_rule(base_action):
    rule = DuplicateActionRule()
    # Same action twice in the batch
    actions = [base_action, base_action.model_copy(deep=True)]
    errors = rule.validate(actions, existing_actions=[])
    
    assert len(errors) == 1
    assert "Duplicate action detected" in errors[0][1]

def test_conflict_rule(base_action):
    rule = ConflictActionRule()
    
    # Conflict: Split and Reverse Split on the same day for same symbol
    action2 = base_action.model_copy(update={"action_type": ActionType.REVERSE_SPLIT, "ratio": 0.5})
    
    errors = rule.validate([base_action, action2], existing_actions=[])
    
    # Both actions are submitted on the same day and conflict with each other
    assert len(errors) == 2
    assert "Conflicting structural actions" in errors[0][1]

def test_effective_date_rule(base_action):
    rule = EffectiveDateRule()
    
    # Future date
    future_action = base_action.model_copy(update={"effective_date": date.today() + timedelta(days=5)})
    
    errors = rule.validate([future_action], existing_actions=[])
    assert len(errors) == 1
    assert "is in the future" in errors[0][1]

def test_ratio_validity_rule(base_action):
    rule = RatioValidityRule()
    
    bad_split = base_action.model_copy(update={"ratio": -1.0})
    bad_div = base_action.model_copy(update={"action_type": ActionType.CASH_DIVIDEND, "ratio": None, "amount": 0.0})
    
    errors = rule.validate([bad_split, bad_div], existing_actions=[])
    assert len(errors) == 2
    assert "Invalid ratio" in errors[0][1]
    assert "Invalid amount" in errors[1][1]

def test_validation_engine(base_action):
    engine = ValidationEngine()
    
    bad_split = base_action.model_copy(update={"ratio": -1.0, "id": "new-uuid", "effective_date": date(2024, 1, 5)})
    
    valid, errors = engine.validate([base_action, bad_split], existing_actions=[])
    
    assert len(valid) == 1
    assert len(errors) == 1
    assert valid[0].id == base_action.id
    assert bad_split.id in [e[0].id for e in errors]
